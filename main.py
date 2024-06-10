import sys
import json
import random
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, Qt
from object import InteractableObject
from pet import VirtualPet

RESOLUTION:list[int] = [1366, 768]
CLOCK_TICK:int = 33     # Clock refresh rate (in milliseconds)
PET_SIZE:int = 150      # Size of the pet (in pixels)
STA_SIZE:int = 65       # Size of the pet's status (in pixels)
OBJ_SIZE:int = 50       # Size of the objects (in pixels)
GRAVITY:int = 4         # Objects' falling speed (in pixels)
FLOOR:int = 637         # Y coordinate for ground level

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.drag_offset = QtCore.QPoint()
        self.is_Interacting:bool = False
        self.is_DraggingPet:bool = False
        self.is_DraggingObj:bool = False

        self.init_userInterface()
        self.init_virtualPet("Slugma", "slug", 1, FLOOR)
        self.init_interactableObject("beach_ball", 1, 1)
        self.init_internalClock()
        
    def update_environment(self):
        self.pet.tick()
        self.falling_check()
        
        if not self.is_DraggingPet:
            self.pet.move()
            
            if not self.pet.is_Sleeping:
                self.wonder_check()
                    
                if not self.pet.is_Wondering:
                    self.reaching_edge_check()
                    self.object_nearby_check()                    

        if not self.is_DraggingObj:
            self.object.move()

        self.scale_labels()
        self.update_labels()

    def wonder_check(self) -> None:              
        if self.pet.is_Wondering:
            if random.random() < 0.01:
                self.pet.wakeUp()
                if random.choice([True, False]):
                    self.pet.turnAround()
        else:
            if random.random() < 0.003:
                self.pet.wonder()    
    
    def reaching_edge_check(self) -> None:
        if self.pet.current_position[0] >= self.width() - PET_SIZE or self.pet.current_position[0] <= 0:
            self.pet.turnAround()

    def check_out_of_bounds(self) -> None:
        if self.pet.current_position[0] > self.width() - PET_SIZE:
            self.pet.current_position[0] = self.width() - PET_SIZE - 1
        if self.pet.current_position[0] < 0:
            self.pet.current_position[0] = 1
        if self.pet.current_position[1] > FLOOR:
            self.pet.current_position[1] = FLOOR

        if self.object.current_position[0] < 0:
            self.object.current_position[0] = 1
        if self.object.current_position[0] > self.width() - OBJ_SIZE:
            self.object.current_position[0] = self.width() - OBJ_SIZE - 1
        if self.object.current_position[1] > FLOOR+82:
            self.object.current_position[1] = FLOOR+82

    def falling_check(self) -> None:
        if not self.is_DraggingPet:
            if self.pet.current_position[1] < FLOOR:
                self.pet.vertical_speed += GRAVITY
                self.pet.fall()
        
            if self.pet.current_position[1] > FLOOR:
                self.pet.current_position[1] = FLOOR
                self.pet.land()

        if not self.is_DraggingObj:
            if self.object.current_position[1] < FLOOR+82:
                self.object.vertical_speed += GRAVITY

            if self.object.current_position[1] > FLOOR+82:
                self.object.horizontal_speed = round(self.object.horizontal_speed*0.7)
                self.object.current_position[1] = FLOOR+82
                self.object.floor_bounce()
            
            if self.object.current_position[0] < 0:
                self.object.current_position[0] = 1
                self.object.wall_bounce()

            if self.object.current_position[0] > self.width() - OBJ_SIZE:
                self.object.current_position[0] = self.width() - OBJ_SIZE - 1
                self.object.wall_bounce()

            if self.object.current_position[1] == FLOOR+82:
                if abs(self.object.horizontal_speed) > 2:
                    self.horizontal_speed = round(self.object.horizontal_speed*0.9)
                else:
                    self.object.horizontal_speed = 0
    
    def object_nearby_check(self) -> None:
        self.object_location = self.object_label.geometry()
        self.pet_location = self.pet_label.geometry()

        if (self.pet_location.contains(self.object_location)):
            match self.object.object_type:
                case "beach_ball":
                    self.object.set_speed_vector(self.pet.kick())
                case _:
                    return

    def update_labels(self) -> None:
        self.pet_label.move(self.pet.current_position[0], self.pet.current_position[1])
        self.status_label.move(self.pet.current_position[0] + PET_SIZE, self.pet.current_position[1])
        self.object_label.move(self.object.current_position[0], self.object.current_position[1])

    def scale_labels(self) -> None:
        self.pet_pixmap = QPixmap(self.pet.get_pet_sprite())
        pet_scaled_pixmap = self.pet_pixmap.scaled(PET_SIZE, PET_SIZE, self.keepAspectRatio, self.transformationMode)
        self.pet_label.setPixmap(pet_scaled_pixmap)

        self.status_pixmap = QPixmap(self.pet.get_status_sprite())
        status_scaled_pixmap = self.status_pixmap.scaled(STA_SIZE, STA_SIZE, self.keepAspectRatio, self.transformationMode)
        self.status_label.setPixmap(status_scaled_pixmap)        

    def init_virtualPet(self, name:str, type:str, x:int, y:int) -> None:
        self.pet = VirtualPet(name, type, x, y)
        self.pet_pixmap = QPixmap(self.pet.get_pet_sprite())
        self.status_pixmap = QPixmap(self.pet.get_status_sprite())

    def init_interactableObject(self, type:str, x:int, y:int) -> None:
        self.object = InteractableObject(type, x, y)
        self.object_pixmap = QPixmap(self.object.get_object_sprite())
        object_scaled_pixmap = self.object_pixmap.scaled(OBJ_SIZE, OBJ_SIZE, self.keepAspectRatio, self.transformationMode)
        self.object_label.setPixmap(object_scaled_pixmap)

    def init_userInterface(self) -> None:
        self.setWindowTitle("Virtual Pet")
        self.setWindowIcon(QtGui.QIcon("resources/sprites/slug_icon.png"))
        self.setGeometry(0, 0, RESOLUTION[0], RESOLUTION[1])
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(1)
        
        self.keepAspectRatio = Qt.AspectRatioMode.KeepAspectRatio
        self.transformationMode = Qt.TransformationMode.SmoothTransformation

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(1, FLOOR, PET_SIZE, PET_SIZE)
        self.pet_location = self.pet_label.geometry()
        
        self.status_label = QLabel(self)
        self.status_label.setGeometry(PET_SIZE + 1, FLOOR, STA_SIZE, STA_SIZE)

        self.object_label = QLabel(self)
        self.object_label.setGeometry(1, 1, OBJ_SIZE, OBJ_SIZE)
        self.object_location = self.object_label.geometry()

    def init_internalClock(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_environment)
        self.timer.start(CLOCK_TICK)
        self.update_environment()

    def mousePressEvent(self, event) -> None:
        self.object_location = self.object_label.geometry()
        self.pet_location = self.pet_label.geometry()
        
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_Interacting = False         
            
            if self.object_location.contains(event.pos()):
                self.drag_offset = event.pos() - self.object_location.topLeft()
                self.is_DraggingObj = True
                return

            if self.pet_location.contains(event.pos()):
                self.drag_offset = event.pos() - self.pet_location.topLeft()
                self.is_DraggingPet = True
                return            

        if event.button() == Qt.MouseButton.RightButton:
            if self.pet_location.contains(event.pos()):     
                self.is_Interacting = True     

    def mouseMoveEvent(self, event) -> None:
        if self.is_DraggingObj:
            self.object.current_position[0] = event.pos().x() - self.drag_offset.x()
            self.object.current_position[1] = event.pos().y() - self.drag_offset.y()
           
        if self.is_DraggingPet:
            self.pet.current_position[0] = event.pos().x() - self.drag_offset.x()
            self.pet.current_position[1] = event.pos().y() - self.drag_offset.y()
             
        self.update_labels()
           
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.object.set_speed_vector([0, 0])
            self.pet.vertical_speed = 0
            self.is_DraggingPet = False
            self.is_DraggingObj = False
            self.check_out_of_bounds()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())