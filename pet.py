import random
from object import InteractableObject

SPRITES_PATH:str = "resources/sprites/"

MAX_HAPPINESS:int = 10000   # Happiness upper bound
EDG_HAPPINESS:int = 3000    # Happiness threshold
MAX_HUNGER:int = 10000      # Hunger upper bound
EDG_HUNGER:int = 8000       # Hunger threshold
MAX_SLEEP:int = 30000       # Sleep upper bound
EDG_SLEEP:int = 20000       # Sleep threshold
MAX_SPEED:int = 2           # Pet's base speed (in pixels)

class VirtualPet:
    def __init__(self, name:str, type:str, x:int, y:int) -> None:
        self.creature_name:str = name
        self.creature_type:str = type
        
        self.current_position:list[int] = [x, y]
        self.horizontal_speed:int = MAX_SPEED
        self.vertical_speed:int = 0        
        
        self.happiness:int = MAX_HAPPINESS
        self.hunger:int = 0
        self.sleep:int = 0
        
        self.is_Wondering:bool = False
        self.is_Sleeping:bool = False
        self.is_Right:bool = True
        
        self.pet_sprite:str = SPRITES_PATH + type +"_default_right.png"
        self.status_sprite:str = SPRITES_PATH +"blank.png"

    def tick(self) -> None:
        if not self.is_Sleeping: 
            if self.sleep < MAX_SLEEP:
                self.sleep += 1
            else:
                self.passOut()        
        else:
            if self.sleep > 0:
                self.sleep -= 7
            else:
                self.wakeUp()

        if self.hunger < MAX_HUNGER:
            self.hunger += 1
        else:
            if self.happiness > 0:
                self.happiness -= 5

        self.happiness -= 1 if self.happiness > 0 else 0
        
        self.clean_internal_state()
        self.update_status_sprite()

    def clean_internal_state(self) -> None:
        if self.happiness > MAX_HAPPINESS:
            self.happiness = MAX_HAPPINESS

        if self.sleep < 0:
            self.sleep = 0

        if self.hunger < 0:
            self.hunger = 0
    
    def update_status_sprite(self) -> None:
        if self.isTired() or self.is_Sleeping:
            self.status_sprite = SPRITES_PATH +"status_tired.png"
            return
        
        if self.isHungry():
            self.status_sprite = SPRITES_PATH +"status_hungry.png"
            return 
        
        self.status_sprite = SPRITES_PATH +"blank.png"

    def update_pet_sprite(self, current_state:str) -> None:
        partial_path:str = SPRITES_PATH + self.creature_type +"_"+ current_state        
        self.pet_sprite = partial_path +"_right.png" if self.is_Right else partial_path +"_left.png"
    
    def isSad(self) -> bool:
        return True if self.happiness <= EDG_HAPPINESS else False
    
    def isHungry(self) -> bool:
        return True if self.hunger >= EDG_HUNGER else False
    
    def isTired(self) -> bool:
        return True if self.sleep >= EDG_SLEEP else False
    
    def move(self) -> None:
        self.current_position[0] += self.horizontal_speed
        self.current_position[1] += self.vertical_speed
    
    def turnAround(self) -> None:
        self.is_Right = not self.is_Right
        self.update_pet_sprite("default")
        self.horizontal_speed *= -1

    def wonder(self) -> None:
        self.is_Wondering = True
        self.update_pet_sprite("wondering")
        self.horizontal_speed = 0
    
    def passOut(self) -> None:
        self.is_Sleeping = True
        self.update_pet_sprite("sleeping")
        self.horizontal_speed = 0
    
    def wakeUp(self) -> None:
        self.is_Wondering = False
        self.is_Sleeping = False
        self.update_pet_sprite("default")
        self.horizontal_speed = MAX_SPEED if self.is_Right else -MAX_SPEED
    
    def fall(self) -> None:
        self.is_Wondering = False
        self.is_Sleeping = False
        self.update_pet_sprite("falling")
        self.horizontal_speed = 0
        
    def land(self) -> None:
        self.update_pet_sprite("default")
        self.horizontal_speed = MAX_SPEED if self.is_Right else -MAX_SPEED
        self.vertical_speed = 0

    def play(self, object_type:str) -> list[int]:
        if object_type == "beach_ball":
            self.happiness += 50
            return self.kick()
    
    def kick(self, object:InteractableObject) -> None:
        x:int = random.randint(30, 50)
        y:int = random.randint(-70, -50)
        speed_vector:list[int] = [x, y] if self.is_Right else [-x, y]
        object.set_speed_vector(speed_vector)
        self.happiness += 100

    def eat(self, object:InteractableObject) -> None:
        self.happiness += 100
        self.hunger -= 1000
        object.destroy()
    
    def get_pet_sprite(self) -> str:
        return self.pet_sprite
    
    def get_status_sprite(self) -> str:
        return self.status_sprite

    