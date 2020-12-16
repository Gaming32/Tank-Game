import pygame


def rot_center(image: pygame.Surface, angle: int, x: int, y: int) -> tuple[pygame.Surface, pygame.Rect]:
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect
