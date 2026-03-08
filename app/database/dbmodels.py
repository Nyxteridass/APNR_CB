import enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String 
from sqlalchemy import Enum as SQLEnum


# Κλάσεις με τα entities που θα δημιουργηθούν στη ΒΔ μας. Η SQLAlchemy αναλαμβάνει τη δημιουργία των πινάκων
# και των πεδίων τους, καθώς και τη διαχείριση των queries.

class Base(DeclarativeBase):
    pass

class UserRole(str , enum.Enum):
    USER = "USER"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMINISTRATOR"
    


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False) # Hashed
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default= UserRole.USER)


class VehicleStatus(str ,enum.Enum):
    STOLEN = "STOLEN"
    WANTED = "WANTED"
    CLEAN = "CLEAN"


class StolenVehicle(Base):
    __tablename__ = "stolen_vehicles"
    plate_number: Mapped[str] = mapped_column(primary_key=True)
    # Χρησιμοποιούμε SQLEnum για τη βάση και το VehicleStatus για την Python
    status: Mapped[VehicleStatus] = mapped_column(SQLEnum(VehicleStatus), default=VehicleStatus.CLEAN)
