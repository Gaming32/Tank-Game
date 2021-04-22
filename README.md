# Tank Game

## Running the game

To play the game you need Python 3.9 or later installed, and you must install (with upgrades!) the packages in requirements.txt.
Then run main.py in the root directory of this repo.

```shell
python3.9 -m pip install -Ur requirements.txt
python3.9 main.py
```

## Playing the game

Your goal is to destroy as many enemy tanks as you can before getting destroyed yourself.

The controls are fairly simple: aim the turret with your mouse, and shoot with left click. To move, use the WASD keys.

+ W will move the tank forward
+ S will move the tank backward
+ A will turn the tank to the left
+ D will turn the tank to the right

Pressing F3 will open the debug screen

## Required assignment stuff

### String manipulation

I manipulate strings in tank_game/main.py:180, where I tell the user how many seconds they survived.

```python
178        screen.blit(rendered, dest_rect)
179
180        rendered = config.FINAL_INFO_BODY_FONT.render(f'And you survived for {global_vars.time_lasted:.3f} seconds', True, 'darkgreen')
181        dest_rect = rendered.get_rect()
182        dest_rect.x = 960 - dest_rect.centerx
```

### Events

I use events in the event loop (tank_game/main.py:72-100) to handle clicks and key presses.

```python
 72    for event in pygame.event.get():
 73        if event.type == QUIT:
 74            running = False
 75        elif event.type == KEYDOWN:
 76            if event.key == K_w:
 77                move_dir = 1
 78            elif event.key == K_s:
 79                move_dir = -1
 80            elif event.key == K_a:
 81                rotate_dir = -1
 82            elif event.key == K_d:
 83                rotate_dir = 1
 84            elif event.key == K_F3:
 85            # elif (event.key == K_f) and (event.mod & KMOD_ALT) and (event.mod & KMOD_SHIFT):
 86                global_vars.debug = not global_vars.debug
 87            elif event.key == K_SPACE:
 88                if death_screen_open:
 89                    death_screen_close = True
 90        elif event.type == KEYUP:
 91            if event.key in (K_w, K_s):
 92                move_dir = 0
 93            elif event.key in (K_a, K_d):
 94                rotate_dir = 0
 95        elif event.type == MOUSEBUTTONDOWN:
 96            if event.button == 1:
 97                if death_screen_open:
 98                    death_screen_close = True
 99                else:
100                    shot_active = True
```

### Functions

I used a function (method actually) in tank_game/tank.py:196-217. This function calculates if a tank will collide with another tank in front (or behind) it.

```python
196    def get_collision(self, dist: int, within: int, angle: int, tanks: list[Tank]) -> tuple[bool, float, Tank]:
197        if dist == 0:
198            return False
199        if dist > 0:
200            rel_angle = 0
201        else:
202            rel_angle = 180
203        ver_angle = angle + rel_angle
204        ver_angle_lt = (ver_angle - 45) % 360
205        ver_angle_gt = (ver_angle + 45) % 360
206        close_dist = inf
207        close_tank = None
208        for other in tanks:
209            if other is self:
210                continue
211            ang = (other.position - self.position).as_polar()[1] + 90
212            ang %= 360
213            if ver_angle_lt < ang < ver_angle_gt:
214                if (tdist := self.position.distance_squared_to(other.position)) < close_dist:
215                    close_dist = tdist
216                    close_tank = other
217        return close_dist <= within, close_dist, close_tank
```
