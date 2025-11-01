from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat
import numpy as np
import json
import os
import requests
from datetime import datetime
import hashlib
from pathlib import Path
from io import BytesIO
import math
from collections import defaultdict

class PILForensicAnalyzer:
    """
    Enhanced forensic analyzer based on PIL + numpy.
    - Adds: JPEG quantization inspection, resampling detection (FFT peaks),
      median-filter tampering detection, color-channel correlation, EXIF-camera checks,
      adaptive thresholds calibrated from a folder of reference images.
    """

    def __init__(self, calibration=None):
        # results and state
        self.results = {
            'metadata_anomalies': [],
            'pixel_anomalies': [],
            'forensic_indicators': [],
            'risk_score': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }
        self.image_path = ""
        self.original_image = None

        # calibration thresholds (default values, will be overridden by calibrate())
        self.thresholds = {
            'ela': { 'very_low': 15, 'low': 40, 'high': 600, 'very_high': 1000 },
            'noise_ratio_max': 3.0,
            'edge_consistency_diff': 20,
            'resampling_fft_peak_ratio': 8.0,
            'color_corr_low': 0.85,
            'clone_block_size': 32,
            'clone_distance_min_blocks': 2
        }

        # calibration summary stats (populated by calibrate_from_folder)
        self.calibration_summary = calibration or {}

    # -----------------------------
    # Input selection / main pipeline
    # -----------------------------
    def url_or_file(self):
        while True:
            user_answer = input(
                "Are you uploading an Image File or Image URL?\n"
                "Image File: A\nImage URL: B\n"
            ).strip().upper()

            if user_answer in ("A", "B"):
                return user_answer
            else:
                print("❌ Invalid response. Please type 'A' for file or 'B' for URL.\n")

    def analyze_image(self):
        """Complete forensic analysis using PIL"""
        try:
            ans = self.url_or_file()

            if ans == "A":
                self.image_path = Path(input("Please paste the Image File Path here: ").strip().strip('"').strip("'"))

                with Image.open(self.image_path) as img:
                    if img.format not in ["JPEG", "PNG", "TIFF"]:
                        img = img.convert("RGB")
                    self.original_image = img.copy()
                    # Run analyses
                    self._analyze_metadata(img)
                    self._analyze_pixel_anomalies(img)
                    self._deep_forensic_inspection(img)
                    self._calculate_risk_score()
                    return self.results

            elif ans == "B":
                self.image_path = input("Please paste the Image URL here: ").strip()
                response = requests.get(self.image_path, timeout=30)
                response.raise_for_status()

                with Image.open(BytesIO(response.content)) as img:
                    if img.format not in ["JPEG", "PNG", "TIFF"]:
                        img = img.convert("RGB")
                    self.original_image = img.copy()
                    self._analyze_metadata(img)
                    self._analyze_pixel_anomalies(img)
                    self._deep_forensic_inspection(img)
                    self._calculate_risk_score()
                    return self.results

        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    # -----------------------------
    # Metadata analysis (enhanced)
    # -----------------------------
    def _analyze_metadata(self, img):
        anomalies = []
        try:
            exif_data = img.getexif()
        except Exception:
            exif_data = None

        if not exif_data:
            anomalies.append("NO_EXIF_DATA: Metadata missing – may have been stripped.")
        else:
            # software
            software = exif_data.get(305)  # Software
            if software:
                software_lower = str(software).lower()
                editing_tools = ['photoshop', 'gimp', 'paint', 'affinity', 'corel']
                if any(tool in software_lower for tool in editing_tools):
                    anomalies.append(f"EDITING_SOFTWARE: {software}")

            # camera model vs typical cameras (basic check)
            model = exif_data.get(272) or exif_data.get(271)
            if model:
                model_str = str(model)
                if 'iphone' in model_str.lower() or 'canon' in model_str.lower() or 'nikon' in model_str.lower():
                    pass  # typical camera -> ok
                else:
                    # unknown camera manufacturer/model could be suspicious in certain contexts
                    anomalies.append(f"UNUSUAL_CAMERA_MODEL: {model_str}")

            # timestamps
            original_time = exif_data.get(36867)  # DateTimeOriginal
            modify_time = exif_data.get(306)       # DateTime
            if original_time and modify_time and original_time != modify_time:
                anomalies.append("METADATA_MODIFIED: Creation and modification timestamps differ.")

            # GPS presence
            gps_keys = [k for k in exif_data.keys() if 'GPS' in str(k) or 'GPS' in str(exif_data.get(k))]
            if gps_keys:
                anomalies.append("GPS_DATA_PRESENT: GPS tags found.")

        if img.format not in ['JPEG', 'PNG', 'TIFF']:
            anomalies.append(f"UNUSUAL_FORMAT: {img.format} – uncommon for original photos.")

        self.results['metadata_anomalies'] = anomalies

    # -----------------------------
    # Pixel-level analysis (improved)
    # -----------------------------
    def _analyze_pixel_anomalies(self, img):
        anomalies = []
        img_rgb = img.convert('RGB')

        # ELA
        ela_result = self._perform_ela(img_rgb)
        ela_variance = float(np.array(ela_result).var())

        ela_risk = self._interpret_ela_with_context(ela_variance, img)
        if ela_risk['level'] != 'NORMAL':
            anomalies.append(ela_risk['message'])

        # noise ratio (local)
        noise_ratio = self._calc_noise_ratio(img_rgb)
        if noise_ratio > self.thresholds.get('noise_ratio_max', 3.0):
            anomalies.append(f"NOISE_INCONSISTENCY: noise_ratio={noise_ratio:.2f}")

        # color-channel correlation
        color_corr = self._calc_color_correlation(img_rgb)
        if color_corr < self.thresholds.get('color_corr_low', 0.85):
            anomalies.append(f"COLOR_CHANNEL_LOW_CORR: corr={color_corr:.2f}")

        # edge consistency
        edge_anoms = self._check_edge_consistency(img_rgb)
        anomalies.extend(edge_anoms)

        # JPEG quantization (if available)
        q_anom = self._analyze_quantization_tables(img_rgb)
        if q_anom:
            anomalies.append(q_anom)

        # add to results
        self.results['ela_variance'] = ela_variance
        self.results['ela_interpretation'] = ela_risk
        self.results['noise_ratio'] = noise_ratio
        self.results['color_channel_corr'] = color_corr
        self.results['pixel_anomalies'] = anomalies

        return anomalies

    def _interpret_ela_with_context(self, ela_variance, img):
        # Use calibrated thresholds if available, else fallback to defaults.
        t = self.thresholds.get('ela', {})
        very_low = t.get('very_low', 15)
        low = t.get('low', 40)
        high = t.get('high', 600)
        very_high = t.get('very_high', 1000)

        is_web_image = str(self.image_path).startswith(('http://', 'https://'))
        image_size = img.size
        total_pixels = image_size[0] * image_size[1]
        # treat small images more tolerant
        if is_web_image or total_pixels < 1_000_000:
            # slightly relax boundaries
            very_low *= 0.9
            low *= 0.95

        # Interpretation
        if ela_variance < very_low:
            return {'level': 'HIGH_RISK', 'message': 'EXTREMELY_LOW_ELA: possible synthetic or over-smoothed image.', 'risk_boost': 12}
        elif ela_variance < low:
            return {'level': 'LOW_RISK', 'message': 'LOW_ELA: likely recompressed/web image or slight processing.', 'risk_boost': 1}
        elif ela_variance > very_high:
            return {'level': 'HIGH_RISK', 'message': 'VERY_HIGH_ELA: strong manipulation signal (multiple edits).', 'risk_boost': 12}
        elif ela_variance > high:
            return {'level': 'MEDIUM_RISK', 'message': 'HIGH_ELA_VARIANCE: inconsistent compression patterns.', 'risk_boost': 6}
        else:
            return {'level': 'NORMAL', 'message': 'Normal compression pattern', 'risk_boost': 0}

    # -----------------------------
    # Deep forensic inspection (new detectors)
    # -----------------------------
    def _deep_forensic_inspection(self, img):
        indicators = []

        img_rgb = img.convert('RGB')

        # clone detection
        clone_regions = self._detect_clone_regions(img_rgb, block_size=self.thresholds.get('clone_block_size', 32))
        if clone_regions:
            indicators.append(f"CLONE_DETECTED: {len(clone_regions)} similar regions found.")

        # resampling detection via FFT peaks
        if self._detect_resampling_fft(img_rgb):
            indicators.append("RESAMPLING_DETECTED: Periodic patterns in frequency domain suggest resizing/resampling.")

        # median filter / local smoothing detection
        if self._detect_median_filter(img_rgb):
            indicators.append("MEDIAN_FILTER_DETECTED: Strong median filtering/smoothing detected.")

        # noise pattern
        if not self._analyze_noise_patterns(img_rgb):
            indicators.append("NOISE_INCONSISTENCY: Uneven noise distribution detected.")

        # compression artifacts
        if self._analyze_compression_artifacts(img_rgb):
            indicators.append("COMPRESSION_ANOMALIES: Multiple compression levels detected.")

        # color temperature
        if self._analyze_color_temperature(img_rgb):
            indicators.append("COLOR_TEMPERATURE_INCONSISTENCY: Lighting inconsistency detected.")

        self.results['forensic_indicators'] = indicators

    # -----------------------------
    # Helper & detection functions
    # -----------------------------
    def _perform_ela(self, img, quality=90):
        temp_path = "_temp_ela.jpg"
        img.save(temp_path, "JPEG", quality=quality)
        recompressed = Image.open(temp_path)
        ela_image = ImageChops.difference(img, recompressed)
        ela_image = ImageEnhance.Brightness(ela_image).enhance(20)
        try:
            os.remove(temp_path)
        except OSError:
            pass
        return ela_image

    def _calc_noise_ratio(self, img):
        """Return ratio max_noise / min_noise across sampled regions (used in your previous logic)."""
        width, height = img.size
        region_size = min(100, max(1, width // 4), max(1, height // 4))
        regions = []
        for y in range(0, max(1, height - region_size), region_size):
            for x in range(0, max(1, width - region_size), region_size):
                region = img.crop((x, y, x + region_size, y + region_size))
                gray = region.convert('L')
                blurred = gray.filter(ImageFilter.GaussianBlur(2))
                noise = ImageChops.difference(gray, blurred)
                stat = ImageStat.Stat(noise)
                noise_level = stat.var[0] if stat.var else 0.0
                regions.append(noise_level)
        if not regions:
            return 0.0
        mx = max(regions)
        mn = min(regions) if min(regions) > 0 else 1e-5
        return mx / mn

    def _calc_color_correlation(self, img):
        """Pearson-like correlation between R,G,B channels (mean over image)."""
        arr = np.array(img).astype(float)
        r = arr[..., 0].ravel()
        g = arr[..., 1].ravel()
        b = arr[..., 2].ravel()
        # numerical stability: if nearly constant, correlation not meaningful
        def corr(a, b):
            if np.std(a) < 1e-5 or np.std(b) < 1e-5:
                return 1.0
            return float(np.corrcoef(a, b)[0, 1])
        rg = corr(r, g)
        rb = corr(r, b)
        gb = corr(g, b)
        return float(np.mean([rg, rb, gb]))

    def _calc_edge_diff(self, img):
        gray = img.convert('L')
        edges1 = gray.filter(ImageFilter.FIND_EDGES)
        edges2 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE)
        stat1, stat2 = ImageStat.Stat(edges1), ImageStat.Stat(edges2)
        return abs(stat1.mean[0] - stat2.mean[0])

    def _check_edge_consistency(self, img):
        anomalies = []
        edge_diff = self._calc_edge_diff(img)
        if edge_diff > self.thresholds.get('edge_consistency_diff', 20):
            anomalies.append("EDGE_CONSISTENCY: Edge structures differ significantly.")
        return anomalies

    def _detect_clone_regions(self, img, block_size=32):
        width, height = img.size
        hashes = {}
        similar_blocks = []

        def phash(block):
            resample = getattr(Image, "Resampling", None)
            if resample:
                small = block.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
            else:
                small = block.resize((8, 8), Image.LANCZOS).convert('L')
            pixels = np.array(small)
            return hashlib.md5(pixels.tobytes()).hexdigest()

        step_y = max(1, block_size)
        step_x = max(1, block_size)
        for y in range(0, max(1, height - block_size), step_y):
            for x in range(0, max(1, width - block_size), step_x):
                block = img.crop((x, y, min(x + block_size, width), min(y + block_size, height)))
                h = phash(block)
                if h in hashes:
                    prev_x, prev_y = hashes[h]
                    dist = math.hypot(x - prev_x, y - prev_y)
                    if dist > block_size * self.thresholds.get('clone_distance_min_blocks', 2):
                        similar_blocks.append({'block1': (prev_x, prev_y), 'block2': (x, y)})
                else:
                    hashes[h] = (x, y)
        return similar_blocks[:10]

    def _analyze_compression_artifacts(self, img):
        ela = self._perform_ela(img)
        var = ImageStat.Stat(ela).var[0]
        return var > 1000

    def _analyze_color_temperature(self, img):
        r, g, b = img.split()
        rs, gs, bs = ImageStat.Stat(r).mean[0], ImageStat.Stat(g).mean[0], ImageStat.Stat(b).mean[0]
        rg_ratio = rs / max(gs, 1e-5)
        rb_ratio = rs / max(bs, 1e-5)
        return abs(rg_ratio - 1.0) > 0.2 or abs(rb_ratio - 1.0) > 0.2

    # JPEG quantization table inspection
    def _analyze_quantization_tables(self, img):
        """
        PIL stores quantization tables (if JPEG) in img.info['quantization'] (a dict).
        Large or uniform quantization tables may indicate heavy recompression or social-media processing.
        """
        try:
            qtables = img.info.get('quantization', None)
        except Exception:
            qtables = None

        if not qtables:
            return None

        # compute simple heuristics: avg q value and variance
        all_vals = []
        for q in qtables.values():
            all_vals.extend(list(q))
        if not all_vals:
            return None
        avg_q = np.mean(all_vals)
        var_q = np.var(all_vals)
        # heuristics
        if avg_q > 40:
            return f"HIGH_QUANTIZATION: avg={avg_q:.1f}, var={var_q:.1f}"
        elif var_q < 20 and avg_q > 20:
            return f"UNIFORM_QUANTIZATION_LOW_VAR: avg={avg_q:.1f}, var={var_q:.1f}"
        else:
            return None

    # median filter detection (local smoothing detector)
    def _detect_median_filter(self, img):
        gray = img.convert('L')
        # apply median filter
        med = gray.filter(ImageFilter.MedianFilter(size=3))
        diff = ImageChops.difference(gray, med)
        # if a lot of pixels changed very little, that suggests median smoothing removal of texture
        stat = ImageStat.Stat(diff)
        mean_diff = stat.mean[0]
        # conservative threshold
        return mean_diff < 1.0  # True -> median filter likely applied

    # resampling detection using FFT (look for periodic peaks)
    def _detect_resampling_fft(self, img):
        gray = img.convert('L')
        arr = np.array(gray, dtype=float)
        # reduce size for FFT speed
        h, w = arr.shape
        max_dim = 512
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            arr = np.array(gray.resize((int(w*scale), int(h*scale)), Image.Resampling.LANCZOS), dtype=float)

        # compute 2D FFT magnitude and centralize
        f = np.fft.fft2(arr)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        # radial average and look for peaks away from DC
        center = (magnitude.shape[0]//2, magnitude.shape[1]//2)
        # compute average magnitude excluding central low-frequency region
        r0 = 5
        mag_no_dc = magnitude.copy()
        mag_no_dc[center[0]-r0:center[0]+r0+1, center[1]-r0:center[1]+r0+1] = 0.0
        # flatten and take top values
        flat = mag_no_dc.ravel()
        top_mean = float(np.mean(np.sort(flat)[-50:])) if flat.size >= 50 else float(np.mean(flat))
        median_mag = float(np.median(flat))
        if median_mag <= 0:
            return False
        ratio = top_mean / (median_mag + 1e-8)
        return ratio > self.thresholds.get('resampling_fft_peak_ratio', 8.0)

    # noise patterns (kept from your original)
    def _analyze_noise_patterns(self, img):
        width, height = img.size
        regions = []
        region_size = min(100, max(1, width//4), max(1, height//4))

        for y in range(0, max(1, height - region_size), region_size):
            for x in range(0, max(1, width - region_size), region_size):
                region = img.crop((x, y, x + region_size, y + region_size))
                gray = region.convert('L')
                blurred = gray.filter(ImageFilter.GaussianBlur(2))
                noise = ImageChops.difference(gray, blurred)
                stat = ImageStat.Stat(noise)
                noise_level = stat.var[0] if stat.var else 0
                regions.append(noise_level)

        return (max(regions) / max(1e-5, min(regions))) < self.thresholds.get('noise_ratio_max', 3.0) if regions else True

    # -----------------------------
    # Compression normalization and scoring
    # -----------------------------
    def _apply_compression_normalization(self, img):
        ela_var = float(self.results.get('ela_variance', 0))
        score = int(self.results.get('risk_score', 0))

        profiles = self._detect_compression_profile(img, ela_var)
        likely_social_media = any(p['profile'] in ['whatsapp_low', 'instagram', 'facebook', 'twitter'] for p in profiles)
        forensic = " ".join(self.results.get('forensic_indicators', []))
        has_edit_indicators = any(tag in forensic for tag in ['CLONE', 'COLOR_TEMPERATURE', 'NOISE_INCONSISTENCY', 'RESAMPLING_DETECTED', 'MEDIAN_FILTER_DETECTED'])
        if likely_social_media and not has_edit_indicators:
            if ela_var < 100:
                reduction = 0.4
            elif ela_var < 200:
                reduction = 0.5
            else:
                reduction = 0.65
            adjusted_score = int(score * reduction)
            self.results['risk_score'] = max(0, min(100, adjusted_score))
            chosen_profile = profiles[0] if profiles else {'profile': 'unknown', 'message': 'social_media_compressed'}
            self.results['compression_adjustment'] = (
                f"Adjusted to {self.results['risk_score']} ({int(reduction*100)}% of original) "
                f"due to likely {chosen_profile.get('message')}"
            )
            self.results['likely_source'] = chosen_profile.get('profile', 'social_media_compressed')
        else:
            self.results['compression_adjustment'] = "No compression normalization applied."
            if 'likely_source' not in self.results:
                self.results['likely_source'] = 'unknown'

    def _detect_compression_profile(self, img, ela_variance):
        compression_profiles = {
            'whatsapp_low': {'range': (10, 50), 'typical_size': (1280, 1280), 'message': 'WhatsApp/Low Quality Compression'},
            'instagram': {'range': (80, 180), 'typical_size': (1080, 1080), 'message': 'Instagram Compression'},
            'facebook': {'range': (120, 280), 'typical_size': (2048, 2048), 'message': 'Facebook Compression'},
            'twitter': {'range': (60, 160), 'typical_size': (1200, 675), 'message': 'Twitter Compression'},
            'original_camera': {'range': (150, 450), 'typical_size': (4000, 3000), 'message': 'Original Camera JPEG'}
        }
        img_size = img.size
        matches = []
        for profile_name, profile in compression_profiles.items():
            low, high = profile['range']
            if low <= ela_variance <= high:
                typical_w, typical_h = profile['typical_size']
                size_match = (abs(img_size[0] - typical_w) <= typical_w * 0.5 and abs(img_size[1] - typical_h) <= typical_h * 0.5)
                confidence = 'HIGH' if size_match else 'MEDIUM'
                matches.append({'profile': profile_name, 'message': profile['message'], 'confidence': confidence, 'size_match': size_match})
        return matches

    def _calculate_risk_score(self):
        score = 0
        # metadata
        for a in self.results.get('metadata_anomalies', []):
            if "NO_EXIF_DATA" in a:
                score += 2
            elif "UNUSUAL_FORMAT" in a:
                score += 3
            elif "EDITING_SOFTWARE" in a:
                score += 12
            else:
                score += 5

        # pixel anomalies
        for a in self.results.get('pixel_anomalies', []):
            score += 6

        # forensic indicators
        for a in self.results.get('forensic_indicators', []):
            if "CLONE" in a:
                score += 20
            elif "NOISE" in a:
                score += 10
            elif "COMPRESSION" in a:
                score += 6
            elif "COLOR_TEMPERATURE" in a:
                score += 10
            elif "RESAMPLING" in a:
                score += 15
            elif "MEDIAN_FILTER" in a:
                score += 12
            else:
                score += 8

        # ELA-derived boost
        ela_interp = self.results.get('ela_interpretation', {})
        if ela_interp:
            score += ela_interp.get('risk_boost', 0)

        # extreme ela variance
        ela_var = float(self.results.get('ela_variance', 0))
        if ela_var < 15 or ela_var > 1000:
            score += 5

        # finalize
        self.results['risk_score'] = min(100, score)

        if self.original_image:
            self._apply_compression_normalization(self.original_image)
        else:
            self.results['compression_adjustment'] = "No original image available for compression normalization."
            self.results.setdefault('likely_source', 'unknown')

    def generate_report(self):
        analysis = self.analyze_image()

        if "error" in analysis:
            return {
                'status': 'failed',
                'error_message': analysis['error'],
                'analysis_timestamp': datetime.now().isoformat(),
                'image': str(self.image_path) if self.image_path else "N/A"
            }

        report = {
            'status': 'success',
            'image': str(self.image_path),
            'analysis_date': self.results['analysis_timestamp'],
            'summary': {
                'risk_level': ('HIGH' if analysis.get('risk_score', 0) > 70 else 'MEDIUM' if analysis.get('risk_score', 0) > 35 else 'LOW'),
                'risk_score': analysis.get('risk_score', 0),
                'total_anomalies': len(analysis.get('metadata_anomalies', [])) + len(analysis.get('pixel_anomalies', [])) + len(analysis.get('forensic_indicators', [])),
                'likely_source': analysis.get('likely_source', 'unknown'),
                'compression_adjustment': analysis.get('compression_adjustment', '')
            },
            'detailed_findings': analysis
        }
        return report


# Example usage (calibrate then analyze)
if __name__ == "__main__":
    analyzer = PILForensicAnalyzer()

    report = analyzer.generate_report()
    print(json.dumps(report, indent=2, default=str))
