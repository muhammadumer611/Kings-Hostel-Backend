from typing import Any

from pydantic import BaseModel, Field


class StudentStatisticsSchema(BaseModel):
    total_students: int
    active_students: int
    inactive_students: int
    students_with_room: int
    students_without_room: int
    fee_paid: int
    fee_pending: int


class RoomStatisticsSchema(BaseModel):
    total_rooms: int
    available_rooms: int
    occupied_rooms: int
    total_beds: int
    occupied_beds: int
    available_beds: int


class FeeStatisticsSchema(BaseModel):
    total_fees: int
    pending_count: int
    paid_count: int
    collected_amount: float
    pending_amount: float
    total_late_fee: float


# class ComplaintStatisticsSchema(BaseModel):
#     total_complaints: int
#     pending_complaints: int
#     resolved_complaints: int
#     in_progress_complaints: int


class DashboardOverviewSchema(BaseModel):
    students: StudentStatisticsSchema
    rooms: RoomStatisticsSchema
    fees: FeeStatisticsSchema


class DashboardDataSchema(BaseModel):
    overview: DashboardOverviewSchema

    recent_students: list[dict[str, Any]] = Field(default_factory=list)
    recent_fee_records: list[dict[str, Any]] = Field(default_factory=list)
    recent_complaints: list[dict[str, Any]] = Field(default_factory=list)
    recent_activity_logs: list[dict[str, Any]] = Field(default_factory=list)

    available_rooms: list[dict[str, Any]] = Field(default_factory=list)
    pending_fee_records: list[dict[str, Any]] = Field(default_factory=list)
    overdue_fee_records: list[dict[str, Any]] = Field(default_factory=list)


class DashboardResponseSchema(BaseModel):
    success: bool
    message: str
    data: DashboardDataSchema | None = None
    errors: Any = None