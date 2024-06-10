SPRITES_PATH:str = "resources/sprites/"

class InteractableObject:
    def __init__(self, name:str, type:str, x:int, y:int) -> None:
        self.object_name:str = name
        self.object_type:str = type
        self.existis:bool = True
        
        self.current_position:list[int] = [x, y]
        self.horizontal_speed:int = 0
        self.vertical_speed:int = 0

        self.elasticity:float = 0.7 if name == "beach_ball" else 0.05
        
        self.object_sprite:str = SPRITES_PATH + type +"_"+ name +".png"

    def move(self) -> None:
        self.current_position[0] += self.horizontal_speed
        self.current_position[1] += self.vertical_speed

    def floor_bounce(self) -> None:
        self.vertical_speed *= -1
        self.vertical_speed = round(self.vertical_speed*self.elasticity) if abs(self.vertical_speed) > 4 else 0
        
    def wall_bounce(self) -> None:
        self.horizontal_speed *= -1
        self.horizontal_speed = round(self.horizontal_speed*self.elasticity)

    def set_speed_vector(self, speed_vector:list[int]) -> None:
        self.horizontal_speed = speed_vector[0]
        self.vertical_speed = speed_vector[1]

    def destroy(self) -> None:
        self.existis = False

    def get_object_sprite(self) -> str:
        return self.object_sprite    