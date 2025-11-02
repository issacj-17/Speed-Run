"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
  DragOverEvent,
  useDroppable,
} from "@dnd-kit/core";
import { arrayMove, SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Clock, User, ArrowRight, MoreVertical } from "lucide-react";
import { SortableCard } from "./SortableCard";

interface KanbanCard {
  review_id: string;
  client_name: string;
  client_id: string;
  risk_score: number;
  red_flags_count: number;
  status: "new" | "review" | "flagged" | "resolved";
  assigned_officer: string;
  time_in_queue: string;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
}

interface KanbanBoardDnDProps {
  cards: KanbanCard[];
}

function DroppableColumn({ id, children }: { id: string; children: React.ReactNode }) {
  const { setNodeRef } = useDroppable({ id });
  return <div ref={setNodeRef} className="bg-gray-100 rounded-b-lg p-3 min-h-[500px] space-y-3">{children}</div>;
}

export function KanbanBoardDnD({ cards: initialCards }: KanbanBoardDnDProps) {
  const router = useRouter();
  const [cards, setCards] = useState(initialCards);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>("all");
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolveCardId, setResolveCardId] = useState<string | null>(null);
  const [resolveReason, setResolveReason] = useState("");
  const [showActionMenu, setShowActionMenu] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor)
  );

  const columns = [
    { id: "new", title: "📥 New Cases", status: "new" as const, color: "bg-blue-50" },
    { id: "review", title: "🔍 Under Review", status: "review" as const, color: "bg-purple-50" },
    { id: "flagged", title: "⚠️ Flagged", status: "flagged" as const, color: "bg-orange-50" },
    { id: "resolved", title: "✅ Resolved", status: "resolved" as const, color: "bg-green-50" },
  ];

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;
  
    const activeId = active.id as string;
    const overId = over.id as string;
  
    const activeContainer = findContainer(activeId);
    const overContainer = findContainer(overId);
  
    if (!activeContainer || !overContainer) return;
    
    // If dragging within the same column, let SortableContext handle it
    if (activeContainer.id === overContainer.id) {
      return;
    }
  
    // Moving between different columns
    setCards((prev) => {
      const activeCard = prev.find(c => c.review_id === activeId);
      if (!activeCard) return prev;
      
      // Remove from old position and update status
      const updatedCard = { ...activeCard, status: overContainer.id as KanbanCard['status'] };
      const filteredCards = prev.filter(c => c.review_id !== activeId);
      
      // Find where to insert in the new column
      const overItems = filteredCards.filter((item) => item.status === overContainer.id);
      const overIndex = overItems.findIndex((item) => item.review_id === overId);
      
      // Insert at the appropriate position
      if (overIndex >= 0) {
        const insertIndex = filteredCards.indexOf(overItems[overIndex]);
        filteredCards.splice(insertIndex, 0, updatedCard);
      } else {
        // If dropping on empty column or at the end
        filteredCards.push(updatedCard);
      }
      
      return filteredCards;
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeCard = cards.find((c) => c.review_id === activeId);
    const overContainer = findContainer(overId);

    if (!activeCard || !overContainer) return;

    // Check if moving to a different column
    if (activeCard.status !== overContainer.id) {
      // If moving to resolved, show confirmation modal
      if (overContainer.id === "resolved") {
        setResolveCardId(activeCard.review_id);
        setShowResolveModal(true);
        return;
      } else {
        // Update status for other columns (already done in dragOver, just show notification)
        const card = cards.find((c) => c.review_id === activeId);
        if (card) {
          window.alert(`✅ ${card.client_name} moved to ${overContainer.id.toUpperCase()}`);
        }
      }
    } else {
      // Reordering within the same column
      if (activeId !== overId) {
        setCards((items) => {
          const activeIndex = items.findIndex(i => i.review_id === activeId);
          const overIndex = items.findIndex(i => i.review_id === overId);
          return arrayMove(items, activeIndex, overIndex);
        });
      }
    }
  };

  const findContainer = (id: string) => {
    if (columns.some(col => col.id === id)) {
      return columns.find(col => col.id === id);
    }
    const card = cards.find(c => c.review_id === id);
    if (card) {
      return columns.find(col => col.status === card.status);
    }
    return undefined;
  };
  
  const updateCardStatus = (cardId: string, newStatus: "new" | "review" | "flagged" | "resolved") => {
    setCards((prev) => {
      const cardIndex = prev.findIndex((card) => card.review_id === cardId);
      if (cardIndex === -1) return prev;
      const card = { ...prev[cardIndex], status: newStatus };
      const newCards = [...prev];
      newCards[cardIndex] = card;
      return newCards;
    });
    
    // Show success notification
    const card = cards.find((c) => c.review_id === cardId);
    if (card) {
      window.alert(`✅ ${card.client_name} moved to ${newStatus.toUpperCase()}`);
    }
  };

  const handleQuickAction = (cardId: string, action: string) => {
    const statusMap: Record<string, "new" | "review" | "flagged" | "resolved"> = {
      "start_review": "review",
      "flag": "flagged",
      "resolve": "resolved",
    };

    if (action === "resolve") {
      setResolveCardId(cardId);
      setShowResolveModal(true);
    } else {
      updateCardStatus(cardId, statusMap[action]);
    }
    setShowActionMenu(null);
  };

  const handleResolveConfirm = () => {
    if (resolveCardId && resolveReason.trim()) {
      updateCardStatus(resolveCardId, "resolved");
      const card = cards.find((c) => c.review_id === resolveCardId);
      console.log("Resolved:", {
        cardId: resolveCardId,
        client: card?.client_name,
        reason: resolveReason,
        officer: "Ana Rodriguez",
        timestamp: new Date(),
      });
      setShowResolveModal(false);
      setResolveCardId(null);
      setResolveReason("");
    }
  };

  const getColumnCards = (status: string) => {
    let filtered = cards.filter((card) => card.status === status);
    if (selectedFilter !== "all") {
      filtered = filtered.filter((card) => card.priority === selectedFilter);
    }
    return filtered;
  };

  const getRiskColor = (score: number) => {
    if (score >= 86) return "bg-red-600 text-white";
    if (score >= 71) return "bg-orange-600 text-white";
    if (score >= 41) return "bg-yellow-600 text-white";
    return "bg-green-600 text-white";
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL":
        return "border-red-500 bg-red-50";
      case "HIGH":
        return "border-orange-500 bg-orange-50";
      case "MEDIUM":
        return "border-yellow-500 bg-yellow-50";
      default:
        return "border-gray-300 bg-white";
    }
  };

  const activeCard = activeId ? cards.find((c) => c.review_id === activeId) : null;

  const totalCards = cards.length;
  const newCount = cards.filter((c) => c.status === "new").length;
  const reviewCount = cards.filter((c) => c.status === "review").length;
  const flaggedCount = cards.filter((c) => c.status === "flagged").length;
  const resolvedCount = cards.filter((c) => c.status === "resolved").length;

  return (
    <div>
      {/* Filter Bar */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Filter by Priority:</span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={selectedFilter === "all" ? "default" : "outline"}
              onClick={() => setSelectedFilter("all")}
            >
              All ({totalCards})
            </Button>
            <Button
              size="sm"
              variant={selectedFilter === "CRITICAL" ? "default" : "outline"}
              onClick={() => setSelectedFilter("CRITICAL")}
              className={selectedFilter === "CRITICAL" ? "bg-red-600" : ""}
            >
              Critical
            </Button>
            <Button
              size="sm"
              variant={selectedFilter === "HIGH" ? "default" : "outline"}
              onClick={() => setSelectedFilter("HIGH")}
              className={selectedFilter === "HIGH" ? "bg-orange-600" : ""}
            >
              High
            </Button>
            <Button
              size="sm"
              variant={selectedFilter === "MEDIUM" ? "default" : "outline"}
              onClick={() => setSelectedFilter("MEDIUM")}
            >
              Medium
            </Button>
          </div>
        </div>
        <div className="text-sm text-gray-600">
          {newCount} New • {reviewCount} Review • {flaggedCount} Flagged • {resolvedCount} Resolved
        </div>
      </div>

      {/* Kanban Board with Drag & Drop */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {columns.map((column) => {
            const columnCards = getColumnCards(column.status);

            return (
              <div key={column.id} className="flex flex-col">
                {/* Column Header */}
                <div className={`${column.color} rounded-t-lg p-4 border-b-2 border-gray-300`}>
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">{column.title}</h3>
                    <Badge variant="secondary" className="bg-white">
                      {columnCards.length}
                    </Badge>
                  </div>
                </div>

                {/* Drop Zone */}
                <SortableContext
                  id={column.id}
                  items={columnCards.map((c) => c.review_id)}
                  strategy={verticalListSortingStrategy}
                >
                  <DroppableColumn id={column.id}>
                    {columnCards.length === 0 ? (
                      <div className="text-center py-8 text-gray-400 text-sm">
                        Drop cards here
                      </div>
                    ) : (
                      columnCards.map((card) => (
                        <SortableCard
                          key={card.review_id}
                          card={card}
                          getRiskColor={getRiskColor}
                          getPriorityColor={getPriorityColor}
                          onCardClick={() => router.push(`/compliance/review/${card.review_id}`)}
                          onQuickAction={(action) => handleQuickAction(card.review_id, action)}
                          showActionMenu={showActionMenu === card.review_id}
                          setShowActionMenu={(show) => setShowActionMenu(show ? card.review_id : null)}
                        />
                      ))
                    )}
                  </DroppableColumn>
                </SortableContext>
              </div>
            );
          })}
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeCard && (
            <Card className={`cursor-grabbing border-l-4 ${getPriorityColor(activeCard.priority)} opacity-80`}>
              <CardContent className="p-4">
                <div className="font-semibold text-gray-900">{activeCard.client_name}</div>
                <div className="text-xs text-gray-500">{activeCard.client_id}</div>
              </CardContent>
            </Card>
          )}
        </DragOverlay>
      </DndContext>

      {/* Resolve Confirmation Modal */}
      {showResolveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">✅ Mark Case as Resolved</h3>
            <p className="text-sm text-gray-600 mb-4">
              Please provide a reason for resolving this case:
            </p>
            <textarea
              className="w-full border rounded-lg p-3 text-sm min-h-[100px] focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Enter resolution reason (e.g., 'All documents verified', 'Client approved', 'Risk assessment complete')..."
              value={resolveReason}
              onChange={(e) => setResolveReason(e.target.value)}
              autoFocus
            />
            <div className="flex gap-3 mt-4">
              <Button
                className="flex-1 bg-green-600 hover:bg-green-700"
                onClick={handleResolveConfirm}
                disabled={!resolveReason.trim()}
              >
                Confirm Resolution
              </Button>
              <Button
                className="flex-1"
                variant="outline"
                onClick={() => {
                  setShowResolveModal(false);
                  setResolveCardId(null);
                  setResolveReason("");
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

