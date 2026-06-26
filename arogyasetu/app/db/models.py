from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text,
    CheckConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    language_preference = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    phone = Column(String, nullable=True)
    available = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="clinic")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    patient_phone = Column(String, ForeignKey("patients.phone"), nullable=False)
    slot_time = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(String, default="confirmed")

    clinic = relationship("Clinic", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")


class DoctorCase(Base):
    __tablename__ = "doctor_cases"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'moderate', 'critical')",
            name="ck_doctor_cases_severity",
        ),
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'resolved')",
            name="ck_doctor_cases_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    patient_phone = Column(
        String, ForeignKey("patients.phone"), nullable=False, index=True
    )
    symptoms = Column(Text, nullable=False)
    severity = Column(String, nullable=False, default="low")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")

    patient = relationship("Patient")

