import pygame
from pygame import *
from pygame.font import Font


class Textbox:
    rect: Rect
    font: Font
    color: tuple[Color, Color, Color]
    edge_width: int
    border_radius: int

    text: str

    def __init__(self, rect: Rect, font: Font, fillcolor: Color, bordercolor: Color = None, textcolor: Color = Color(0, 0, 0), edge_width: int = 0, border_radius: int = 0, start_text: str = '') -> None:
        if bordercolor is None:
            bordercolor = fillcolor
        self.rect = rect
        self.font = font
        self.color = (fillcolor, bordercolor, textcolor)
        self.edge_width = edge_width
        self.border_radius = border_radius
        self.text = start_text

    def clear(self):
        self.text = ''

    def render(self, surf: Surface, antialias: bool = True) -> Rect:
        pygame.draw.rect(surf, self.color[0], self.rect, 0, self.border_radius)
        pygame.draw.rect(surf, self.color[1], self.rect, self.edge_width, self.border_radius)
        render = self.font.render(self.text, antialias, self.color[2])
        rrect = render.get_rect()
        newrect = self.rect.copy()
        newrect.x += self.rect.width // 2 - rrect.centerx
        newrect.y += self.rect.height // 2 - rrect.centery
        return surf.blit(render, newrect)

    def handle_key(self, event: pygame.event.Event) -> bool:
        if event.type != KEYDOWN:
            return
        if event.key == K_BACKSPACE:
            if event.mod & KMOD_CTRL:
                res = self.text.rsplit(None, 1)
                if len(res) > 1:
                    self.text = self.text.rsplit(None, 1)[0]
                else:
                    self.text = ''
            else:
                self.text = self.text[:-1]
        elif event.key == K_TAB:
            self.text += '\t'
        elif event.key == K_RETURN:
            return True
        else:
            self.text += event.unicode
        return False
