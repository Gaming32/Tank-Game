from tank_game.leaderboard import LeaderboardManager


DREAMLO_PRIVATE_CODE = '<obfuscated>'
DREAMLO_PUBLIC_CODE = '5fdd39e4eb36c70af8509c7b'


manager = LeaderboardManager(DREAMLO_PRIVATE_CODE, DREAMLO_PUBLIC_CODE)


if __name__ == '__main__':
    import py_compile
    py_compile.compile(__file__, 'tank_game/leaderboard_secrets.pyc')
