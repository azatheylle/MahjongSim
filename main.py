from cmu_graphics import *
import random
app.background = rgb(40, 120, 70)

# Tile format:
# manzu: 1m-9m
# pinzu: 1p-9p
# souzu: 1s-9s
# honors:
#   E = east
#   S = south
#   W = west
#   N = north
#   Wh = white dragon
#   G = green dragon
#   R = red dragon

app.currentPlayer = 0
app.aiTurnDelay = 18
app.aiDelayCounter = 0
app.pendingAiPlayers = []
app.aiThinking = False
app.stepsPerSecond = 30
app.actionPromptOpen = False
app.actionOptions = []
app.actionButtonTargets = []
app.gameMessage = ''
app.handOver = False
app.lastDiscardedTile = None
app.lastDiscarder = None
app.pendingChiOptions = []
app.pendingCallTile = None
app.pendingCallDiscarder = None
app.pendingKanTile = None
app.pendingKanType = None
app.roundResult = None
app.roundResultReason = ''
app.roundScoreText = ''
app.roundYakuLines = []
app.roundWinnerIndex = None
app.noYakuWarning = ''
app.resultButtonTarget = None
app.tutorialOpen = False
app.tutorialPage = 0
app.tutorialButtonTargets = []
app.doraIndicators = []
app.doraTiles = []
app.revealedDoraCount = 1
app.mainPlayerIndex = 0
app.dealerIndex = 0
app.roundWind = 'E'
app.openTanyaoEnabled = True
app.kazoeYakumanEnabled = True

app.currentScene = 'room'

app.playerX = 200
app.playerY = 300
app.playerSize = 18
app.playerSpeed = 4

app.moveUp = False
app.moveDown = False
app.moveLeft = False
app.moveRight = False

app.tableX = 150
app.tableY = 120
app.tableW = 100
app.tableH = 60

app.tutorialNpcX = 55
app.tutorialNpcY = 330
app.tutorialNpcSize = 22

app.handSelectTableX = 250
app.handSelectTableY = 280
app.handSelectTableW = 100
app.handSelectTableH = 60

app.playerNearTable = False
app.playerNearHandSelectTable = False
app.playerNearTutorialNpc = False
app.handSelectionButtonTargets = []
app.customHandInput = ''
app.customHandError = ''

TileIndexMap = {
    '1m': 0, '2m': 1, '3m': 2, '4m': 3, '5m': 4, '6m': 5, '7m': 6, '8m': 7, '9m': 8,
    '1p': 9, '2p': 10, '3p': 11, '4p': 12, '5p': 13, '6p': 14, '7p': 15, '8p': 16, '9p': 17,
    '1s': 18, '2s': 19, '3s': 20, '4s': 21, '5s': 22, '6s': 23, '7s': 24, '8s': 25, '9s': 26,
    'E': 27, 'S': 28, 'W': 29, 'N': 30, 'Wh': 31, 'G': 32, 'R': 33
    }

TileNamesByIndex = [''] * 34
for tileName, tileIndex in TileIndexMap.items():
    TileNamesByIndex[tileIndex] = tileName

TileWidth = 24
TileHeight = 36
TileGap = 2

HandY = 400 - 52

SuitOrder = {'m': 0, 'p': 1, 's': 2}
HonorOrder = {'E': 0, 'S': 1, 'W': 2, 'N': 3, 'Wh': 4, 'G': 5, 'R': 6}
WindOrder = ['E', 'S', 'W', 'N']
DragonTiles = {'Wh', 'G', 'R'}
GreenTiles = {'2s', '3s', '4s', '6s', '8s', 'G'}

ThirteenOrphansTiles = {
    '1m', '9m',
    '1p', '9p',
    '1s', '9s',
    'E', 'S', 'W', 'N', 'Wh', 'G', 'R'
}

app.drawnTile = None

def build_wall():
    wall = []
        
    for suit in ['m', 'p', 's']:
        for number in range(1, 10):
            tile = str(number) + suit
            for copy in range(4):
                wall.append(tile)
                
    for honor in ['E', 'S', 'W', 'N', 'Wh', 'G', 'R']:
        for copy in range(4):
            wall.append(honor)
            
    return wall

def tile_sort_key(tile):
    if tile in HonorOrder:
        return (3, HonorOrder[tile])
        
    number = int(tile[0])
    suit = tile[1]
    return (SuitOrder[suit], number)
        

def sort_hand(hand):
    hand.sort(key=tile_sort_key)

def get_next_dora_tile(indicatorTile):
    if indicatorTile in HonorOrder:
        if indicatorTile == 'E':
            return 'S'
        elif indicatorTile == 'S':
            return 'W'
        elif indicatorTile == 'W':
            return 'N'
        elif indicatorTile == 'N':
            return 'E'
        elif indicatorTile == 'Wh':
            return 'G'
        elif indicatorTile == 'G':
            return 'R'
        elif indicatorTile == 'R':
            return 'Wh'

    number = int(indicatorTile[0])
    suit = indicatorTile[1]
    nextNumber = number + 1
    if nextNumber > 9:
        nextNumber = 1
    return str(nextNumber) + suit

def initialize_dora_state():
    app.doraIndicators = []
    for i in range(4):
        app.doraIndicators.append(random.choice(TileNamesByIndex))

    app.doraTiles = []
    for indicatorTile in app.doraIndicators:
        app.doraTiles.append(get_next_dora_tile(indicatorTile))

    app.revealedDoraCount = 1

def reveal_next_dora_indicator():
    if app.revealedDoraCount < len(app.doraIndicators):
        app.revealedDoraCount += 1

def get_dora_tiles_for_scoring():
    # Reminder for future scoring work: riichi win scoring uses all predetermined dora,
    # including those whose indicators are still hidden on the table.
    return app.doraTiles[:]

def get_revealed_dora_tiles():
    return app.doraTiles[:app.revealedDoraCount]

def tile_is_revealed_dora(tile):
    return tile in get_revealed_dora_tiles()
    
def reset_round_state():
    app.currentPlayer = 0
    app.aiDelayCounter = 0
    app.pendingAiPlayers = []
    app.aiThinking = False
    app.actionPromptOpen = False
    app.actionOptions = []
    app.actionButtonTargets = []
    app.gameMessage = ''
    app.handOver = False
    app.lastDiscardedTile = None
    app.drawnTile = None
    app.selectedHandIndex = None
    app.previewTile = None
    app.lastDiscarder = None
    app.pendingChiOptions = []
    app.pendingCallTile = None
    app.pendingCallDiscarder = None
    app.pendingKanTile = None
    app.pendingKanType = None
    app.roundResult = None
    app.roundResultReason = ''
    app.roundScoreText = ''
    app.roundYakuLines = []
    app.roundWinnerIndex = None
    app.noYakuWarning = ''
    app.resultButtonTarget = None
    app.tutorialOpen = False
    app.tutorialPage = 0
    app.tutorialButtonTargets = []
    app.doraIndicators = []
    app.doraTiles = []
    app.revealedDoraCount = 1
    
def deal_starting_hands():
    newWall = build_wall()
    random.shuffle(newWall)
        

    players = [
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None}
    ]

    for roundNumber in range(13):
        for playerIndex in range(4):
            players[playerIndex]['hand'].append(newWall.pop())
        
    players[0]['hand'].append(newWall.pop())
    
    for player in players:
        sort_hand(player['hand'])
        
    return players, newWall

def validate_and_parse_hand(inputStr):
    """Parse and validate a hand input string like 'E, E, E, 1m, 2p, ...'
    Returns (hand, errorMessage) where hand is None if invalid"""
    
    if not inputStr.strip():
        return None, 'Please enter tiles'
    
    # Parse the input
    tilesToString = inputStr.strip().split(',')
    tiles = []
    
    for tileStr in tilesToString:
        tile = tileStr.strip()
        
        if not tile:
            continue
            
        # Validate tile format
        if tile not in TileIndexMap:
            return None, f'Invalid tile: {tile}'
        
        tiles.append(tile)
    
    # Check tile count
    if len(tiles) != 14:
        return None, f'Need exactly 14 tiles, got {len(tiles)}'
    
    # Check for duplicates (max 4 of any tile)
    tileCounts = {}
    for tile in tiles:
        tileCounts[tile] = tileCounts.get(tile, 0) + 1
        if tileCounts[tile] > 4:
            return None, f'Too many {tile}s (max 4, got {tileCounts[tile]})'
    
    return tiles, None

app.players, app.wall = deal_starting_hands()
app.hand = app.players[app.mainPlayerIndex]['hand']
initialize_dora_state()

# total width of 14 tiles with gaps
app.TotalHandWidth = len(app.hand) * TileWidth + (len(app.hand) - 1) * TileGap 
app.HandX = (400 - app.TotalHandWidth) / 2

app.selectedHandIndex = None
app.previewTile = None
app.clickTargets = []
app.scene = Group()
app.noYakuWarning = ''

def draw_dora_shine(x, y, w, h, rotateAngle=0):
    # Stronger shine so Dora is clearly visible in hand, board mini tiles, and preview.
    app.scene.add(Rect(x + 1, y + 1, w - 2, h - 2, fill=rgb(255, 238, 150), opacity=22, rotateAngle=rotateAngle))
    app.scene.add(Rect(x + 1, y + 1, w - 2, h - 2, fill=None, border=rgb(255, 205, 60), borderWidth=2, opacity=60, rotateAngle=rotateAngle))
    app.scene.add(Circle(x + w * 0.23, y + h * 0.2, max(1.5, w * 0.06), fill='white', opacity=75, rotateAngle=rotateAngle))


def draw_tile_base(x, y, isDora=False):
    app.scene.add(Rect(x, y, TileWidth, TileHeight, fill='white', border='black', borderWidth=1))
    if isDora:
        draw_dora_shine(x, y, TileWidth, TileHeight)
    else:
        app.scene.add(Rect(x + 1, y + 1, TileWidth - 2, TileHeight - 2, fill=rgb(245, 240, 225), opacity=35))
            
            
def draw_center_text(x, y, text, size=11, color='black', bold=False):
    app.scene.add(Label(text, x + TileWidth / 2, y + TileHeight / 2, size=size, fill=color, bold=bold))
                    
                    
def draw_manzu(x, y, number):
    app.scene.add(Label(str(number), x + TileWidth / 2, y + 10, size=12, fill='red', bold=True))
    app.scene.add(Label('M', x + TileWidth / 2, y + 24, size=13, fill='red', bold=True))
                                
                                
def draw_pinzu(x, y, number):
    app.scene.add(Label(str(number), x + TileWidth / 2, y + 8, size=12, fill='blue', bold=True))
    app.scene.add(Label('P', x + TileWidth / 2, y + 24, size=13, fill='blue', bold=True))
                                                                                  

def draw_souzu(x, y, number):
    app.scene.add(Label(str(number), x + TileWidth / 2, y + 8, size=12, fill='green', bold=True))
    app.scene.add(Label('S', x + TileWidth / 2, y + 24, size=13, fill='green', bold=True))
                
                
def draw_honor(x, y, tile):
        if tile == 'E':
            draw_center_text(x, y, 'E', size=15, color='black', bold=True)
        elif tile == 'S':
            draw_center_text(x, y, 'S', size=15, color='black', bold=True)
        elif tile == 'W':
            draw_center_text(x, y, 'W', size=15, color='black', bold=True)
        elif tile == 'N':
            draw_center_text(x, y, 'N', size=15, color='black', bold=True)
        elif tile == 'Wh':
            draw_center_text(x, y, 'Wh', size=15, color='gray', bold=True)
        elif tile == 'G':
            draw_center_text(x, y, 'G', size=15, color='green', bold=True)
        elif tile == 'R':
            draw_center_text(x, y, 'R', size=15, color='red', bold=True)
            
            
def draw_tile(x, y, tile, dimmed=False):
    draw_tile_base(x, y, isDora=tile_is_revealed_dora(tile))
        
    if tile in HonorOrder:
        draw_honor(x, y, tile)
    else:
        number = int(tile[0])
        suit = tile[1]
            
        if suit == 'm':
            draw_manzu(x, y, number)
        elif suit == 'p':
            draw_pinzu(x, y, number)
        elif suit == 's':
            draw_souzu(x, y, number)

    if dimmed:
        app.scene.add(Rect(x, y, TileWidth, TileHeight, fill='lightGray', opacity=55))
                    
                    
def draw_selected_outline(x, y):
    app.scene.add(Rect(x - 1, y - 1, TileWidth + 2, TileHeight + 2, fill=None, border='red', borderWidth=2))
    
def draw_preview_panel():
    app.scene.add(Rect(330, 5, 65, 95, fill='white', border='black', borderWidth=2))

    if app.previewTile != None:
        previewX = 331
        previewY = 6
        tile = app.previewTile
        isDora = tile_is_revealed_dora(tile)
        
        # big boy tile
        app.scene.add(Rect(previewX, previewY, 63, 93, fill='white', border='black', borderWidth=1))
        if isDora:
            draw_dora_shine(previewX, previewY, 63, 93)
        else:
            app.scene.add(Rect(previewX + 1, previewY + 1, 61, 91, fill=rgb(248, 244, 232), opacity=40))
        

        if tile in HonorOrder:
            if tile == 'E':
                app.scene.add(Label('E', previewX + 31, previewY + 47, size=30, fill='black', bold=True))
            elif tile == 'S':
                app.scene.add(Label('S', previewX + 31, previewY + 47, size=30, fill='black', bold=True))
            elif tile == 'W':
                app.scene.add(Label('W', previewX + 31, previewY + 47, size=30, fill='black', bold=True))
            elif tile == 'N':
                app.scene.add(Label('N', previewX + 31, previewY + 47, size=30, fill='black', bold=True))
            elif tile == 'Wh':
                app.scene.add(Label('Wh', previewX + 31, previewY + 47, size=24, fill='gray', bold=True))
            elif tile == 'G':
                app.scene.add(Label('G', previewX + 31, previewY + 47, size=30, fill='green', bold=True))
            elif tile == 'R':
                app.scene.add(Label('R', previewX + 31, previewY + 47, size=30, fill='red', bold=True))

        else:
            number = int(tile[0])
            suit = tile[1]

            if suit == 'm':
                app.scene.add(Label(str(number), previewX + 31, previewY + 26, size=26, fill='red', bold=True))
                app.scene.add(Label('M', previewX + 31, previewY + 63, size=30, fill='red', bold=True))
            elif suit == 'p':
                app.scene.add(Label(str(number), previewX + 31, previewY + 26, size=26, fill='blue', bold=True))
                app.scene.add(Label('P', previewX + 31, previewY + 63, size=30, fill='blue', bold=True))
            elif suit == 's':
                app.scene.add(Label(str(number), previewX + 31, previewY + 26, size=26, fill='green', bold=True))
                app.scene.add(Label('S', previewX + 31, previewY + 63, size=30, fill='green', bold=True))

                        
def draw_mini_tile(x, y, tile, rotateAngle=0, highlightDoraBackground=True):
    isDora = highlightDoraBackground and tile_is_revealed_dora(tile)
    app.scene.add(Rect(x, y, 20, 30, fill='white', border='black', borderWidth=1, rotateAngle=rotateAngle))
    if isDora:
        draw_dora_shine(x, y, 20, 30, rotateAngle=rotateAngle)
    else:
        app.scene.add(Rect(x + 1, y + 1, 18, 28, fill=rgb(248, 244, 232), opacity=40, rotateAngle=rotateAngle))
          
    if tile in HonorOrder:
        color = 'black'
        if tile == 'G':
            color = 'green'
        elif tile == 'R':
            color = 'red'

        app.scene.add(Label(tile, x + 10, y + 15, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
    else:
        number = tile[0]
        suit = tile[1]
        
        color = 'black'
        suitLetter = suit.upper()
        if suit == 'm':
            color = 'red'
        elif suit == 'p':
            color = 'blue'
        elif suit == 's':
            color = 'green'

        if rotateAngle == 90:
            # Left seat POV: number should be center-facing, suit/player color edge-facing.
            app.scene.add(Label(number, x + 15, y + 15, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
            app.scene.add(Label(suitLetter, x + 5, y + 15, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
        elif rotateAngle == -90:
            # Right seat POV: mirror so number remains center-facing.
            app.scene.add(Label(number, x + 5, y + 15, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
            app.scene.add(Label(suitLetter, x + 15, y + 15, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
        else:
            app.scene.add(Label(number, x + 10, y + 9, size=10, fill=color, bold=True, rotateAngle=rotateAngle))
            app.scene.add(Label(suitLetter, x + 10, y + 21, size=10, fill=color, bold=True, rotateAngle=rotateAngle))

def draw_player_calls():
    startRightX = 395
    y = 365
    setGap = 10
    miniTileStep = 22
    
    currentRightX = startRightX
    
    for callIndex in range(len(app.players[0]['calls']) - 1, -1, -1):
        call = app.players[0]['calls'][callIndex]
        tiles = call['tiles']
        
        setWidth = len(tiles) * miniTileStep - 2
        startX = currentRightX - setWidth
        
        for i in range(len(tiles)):
            x = startX + i * miniTileStep
            draw_mini_tile(x, y, tiles[i])
            
        currentRightX = startX - setGap

def draw_dora_indicator_panel():
    panelX = 8
    panelY = 8
    panelW = 110
    panelH = 54
    slotStartX = panelX + 8
    slotY = panelY + 16
    slotGap = 24

    app.scene.add(Rect(panelX, panelY, panelW, panelH, fill=rgb(25, 90, 55), border='white', borderWidth=1))
    app.scene.add(Label('Dora', panelX + panelW / 2, panelY + 10, size=10, fill='white', bold=True))

    for i in range(4):
        slotX = slotStartX + i * slotGap

        if i < app.revealedDoraCount and i < len(app.doraIndicators):
            draw_mini_tile(slotX, slotY, app.doraIndicators[i], highlightDoraBackground=False)
        else:
            app.scene.add(Rect(slotX, slotY, 20, 30, fill=rgb(50, 70, 90), border='black', borderWidth=1))
            app.scene.add(Rect(slotX + 3, slotY + 3, 14, 24, fill=rgb(85, 105, 125), opacity=65))

def draw_recent_discards():
    # top player (player 2)
    topDiscards = app.players[2]['discards']
    
    if len(topDiscards) == 0:
        pass
    
    elif len(topDiscards) == 1:
        tile = topDiscards[-1]
        x = 216
        y = 125
        draw_mini_tile(x, y, tile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': tile, 'x': x, 'y': y, 'w': 20, 'h': 30})
        
    elif len(topDiscards) == 2:
        newestTile = topDiscards[-1]
        olderTile = topDiscards[-2]
        
        draw_mini_tile(216, 125, newestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 216, 'y': 125, 'w': 20, 'h': 30})
        
        draw_mini_tile(192, 125, olderTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': olderTile, 'x': 192, 'y': 125, 'w': 20, 'h': 30})
        
    else:
        visibleTopDiscards = topDiscards[-3:]
        
        newestTile = visibleTopDiscards[-1]
        middleTile = visibleTopDiscards[-2]
        oldestTile = visibleTopDiscards[-3]
        
        draw_mini_tile(216, 125, newestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 216, 'y': 125, 'w': 20, 'h': 30})
        
        draw_mini_tile(192, 125, middleTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': middleTile, 'x': 192, 'y': 125, 'w': 20, 'h': 30})
        
        draw_mini_tile(168, 125, oldestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': oldestTile, 'x': 168, 'y': 125, 'w': 20, 'h': 30})
        
        
    # left player (player 1)
    leftDiscards = app.players[1]['discards']
    
    if len(leftDiscards) == 0:
        pass
    
    elif len(leftDiscards) == 1:
        tile = leftDiscards[-1]
        x = 125
        y = 168
        draw_mini_tile(x, y, tile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': tile, 'x': x, 'y': y, 'w': 20, 'h': 30})
        
    elif len(leftDiscards) == 2:
        newestTile = leftDiscards[-1]
        olderTile = leftDiscards[-2]
        
        draw_mini_tile(125, 168, newestTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 125, 'y': 168, 'w': 20, 'h': 30})
        
        draw_mini_tile(125, 192, olderTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': olderTile, 'x': 125, 'y': 192, 'w': 20, 'h': 30})
        
    else:
        visibleLeftDiscards = leftDiscards[-3:]
        
        newestTile = visibleLeftDiscards[-1]
        middleTile = visibleLeftDiscards[-2]
        oldestTile = visibleLeftDiscards[-3]
        
        draw_mini_tile(125, 168, newestTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 125, 'y': 168, 'w': 20, 'h': 30})
        
        draw_mini_tile(125, 192, middleTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': middleTile, 'x': 125, 'y': 192, 'w': 20, 'h': 30})
        
        draw_mini_tile(125, 216, oldestTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': oldestTile, 'x': 125, 'y': 216, 'w': 20, 'h': 30})
        
    # right player (player 3)
    rightDiscards = app.players[3]['discards']
    
    if len(rightDiscards) == 0:
        pass
    
    elif len(rightDiscards) == 1:
        tile = rightDiscards[-1]
        x = 255
        y = 216
        draw_mini_tile(x, y, tile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': tile, 'x': x, 'y': y, 'w': 20, 'h': 30})
        
    elif len(rightDiscards) == 2:
        newestTile = rightDiscards[-1]
        olderTile = rightDiscards[-2]
        
        draw_mini_tile(255, 216, newestTile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 255, 'y': 216, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 192, olderTile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': olderTile, 'x': 255, 'y': 192, 'w': 20, 'h': 30})
        
    else:
        visibleRightDiscards = rightDiscards[-3:]
        
        newestTile = visibleRightDiscards[-1]
        middleTile = visibleRightDiscards[-2]
        oldestTile = visibleRightDiscards[-3]
        
        draw_mini_tile(255, 216, newestTile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 255, 'y': 216, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 192, middleTile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': middleTile, 'x': 255, 'y': 192, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 168, oldestTile, rotateAngle=-90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': oldestTile, 'x': 255, 'y': 168, 'w': 20, 'h': 30})
        
    # bottom player (player 0)
    bottomDiscards = app.players[0]['discards']
    
    if len(bottomDiscards) == 0:
        pass
    
    elif len(bottomDiscards) == 1:
        tile = bottomDiscards[-1]
        x = 168
        y = 255
        draw_mini_tile(x, y, tile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': tile, 'x': x, 'y': y, 'w': 20, 'h': 30})
        
    elif len(bottomDiscards) == 2:
        newestTile = bottomDiscards[-1]
        olderTile = bottomDiscards[-2]
        y = 255
        draw_mini_tile(168, y, newestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 168, 'y': y, 'w': 20, 'h': 30})    
    
        draw_mini_tile(192, y, olderTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': olderTile, 'x': 192, 'y': y, 'w': 20, 'h': 30})    
    
    else:
        visibleBottomDiscards = bottomDiscards[-3:]
        
        newestTile = visibleBottomDiscards[-1]
        middleTile = visibleBottomDiscards[-2]
        oldestTile = visibleBottomDiscards[-3]
        y = 255
        draw_mini_tile(168, y, newestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 168, 'y': y, 'w': 20, 'h': 30})    
        draw_mini_tile(192, y, middleTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': middleTile, 'x': 192, 'y': y, 'w': 20, 'h': 30})    
        draw_mini_tile(216, y, oldestTile)
        app.clickTargets.append({'type': 'discardPreview', 'tile': oldestTile, 'x': 216, 'y': y, 'w': 20, 'h': 30})    

def build_tile_counts(hand):
    counts = [0] * 34
    for tile in hand:
        counts[TileIndexMap[tile]] += 1
    return counts
    
def can_form_melds(counts):
    firstIndex = -1
    for i in range(34):
        if counts[i] > 0:
            firstIndex = i
            break
        
    if firstIndex == -1:
        return True
        
    if counts[firstIndex] >= 3:
        counts[firstIndex] -= 3
        if can_form_melds(counts):
            counts[firstIndex] += 3
            return True
        counts[firstIndex] += 3
            
    if firstIndex <= 26:
        suitStart = (firstIndex // 9) * 9
        suitOffset = firstIndex - suitStart
        if suitOffset <= 6:
            if counts[firstIndex + 1] > 0 and counts[firstIndex + 2] > 0:
                counts[firstIndex] -= 1
                counts[firstIndex + 1] -= 1
                counts[firstIndex + 2] -= 1
                
                if can_form_melds(counts):
                    counts[firstIndex] += 1
                    counts[firstIndex + 1] += 1
                    counts[firstIndex + 2] += 1
                    return True
                    
                counts[firstIndex] += 1
                counts[firstIndex + 1] += 1
                counts[firstIndex + 2] += 1
                    
    return False
    
def get_player_call_meld_count(playerIndex=0):
    return len(app.players[playerIndex]['calls'])

def is_seven_pairs(hand):
    if len(hand) != 14:
        return False

    counts = build_tile_counts(hand)
    pairCount = 0

    for count in counts:
        if count == 2:
            pairCount += 1
        elif count != 0:
            return False

    return pairCount == 7

def is_thirteen_orphans(hand):
    if len(hand) != 14:
        return False

    counts = build_tile_counts(hand)
    pairFound = False

    for tileIndex, count in enumerate(counts):
        if count == 0:
            continue

        tile = TileNamesByIndex[tileIndex]
        if tile not in ThirteenOrphansTiles:
            return False

        if count == 2:
            if pairFound:
                return False
            pairFound = True
        elif count != 1:
            return False

    if pairFound == False:
        return False

    for tile in ThirteenOrphansTiles:
        if counts[TileIndexMap[tile]] == 0:
            return False

    return True

def is_valid_win_hand(hand, playerIndex=0):
    return is_standard_win_with_calls(hand, playerIndex) or is_seven_pairs(hand) or is_thirteen_orphans(hand)

def hand_is_tenpai_for_riichi(hand, playerIndex=None):
    if playerIndex == None:
        playerIndex = app.mainPlayerIndex

    if player_hand_is_closed(playerIndex) == False:
        return False

    if len(hand) != 14:
        return False

    for discardIndex in range(len(hand)):
        reducedHand = hand[:discardIndex] + hand[discardIndex + 1:]

        for tile in TileIndexMap:
            candidateHand = reducedHand[:] + [tile]
            if is_standard_win(candidateHand):
                return True
            if is_seven_pairs(candidateHand):
                return True
            if is_thirteen_orphans(candidateHand):
                return True

    return False

def is_tenpai_hand(hand):
    if len(hand) != 13:
        return False

    for tile in TileIndexMap:
        candidateHand = hand[:] + [tile]
        if is_valid_win_hand(candidateHand):
            return True

    return False

def get_riichi_legal_discard_indices():
    fullHand = app.hand[:]
    if app.drawnTile != None:
        fullHand.append(app.drawnTile)

    legalIndices = []

    for index in range(len(fullHand)):
        reducedHand = fullHand[:index] + fullHand[index + 1:]
        if is_tenpai_hand(reducedHand):
            legalIndices.append(index)

    return legalIndices

def can_form_partial_melds(counts, meldsNeeded):
    if meldsNeeded == 0:
        for i in range(34):
            if counts[i] != 0:
                return False
        return True
                
    firstIndex = -1
    for i in range(34):
        if counts[i] > 0:
            firstIndex = i
            break
    
    if firstIndex == -1:
        return False
    
    if counts[firstIndex] >= 3:
        counts[firstIndex] -= 3
        if can_form_partial_melds(counts, meldsNeeded - 1):
            counts[firstIndex] += 3
            return True
        counts[firstIndex] += 3
    
    if firstIndex <= 26:
        suitStart = (firstIndex // 9) * 9
        suitOffset = firstIndex - suitStart
        if suitOffset <= 6:
            if counts[firstIndex + 1] > 0 and counts[firstIndex + 2] > 0:
                counts[firstIndex] -= 1
                counts[firstIndex + 1] -= 1
                counts[firstIndex + 2] -= 1
    
                if can_form_partial_melds(counts, meldsNeeded - 1):
                    counts[firstIndex] += 1
                    counts[firstIndex + 1] += 1
                    counts[firstIndex + 2] += 1
                    return True
    
                counts[firstIndex] += 1
                counts[firstIndex + 1] += 1
                counts[firstIndex + 2] += 1
    
    return False

def is_standard_win_with_calls(concealedTiles, playerIndex=0):
    totalMeldsNeededFromHand = 4 - get_player_call_meld_count(playerIndex)
    
    if totalMeldsNeededFromHand < 0:
        return False
        
    expectedTileCount = totalMeldsNeededFromHand * 3 + 2
    if len(concealedTiles) != expectedTileCount:
        return False
        
        
    counts = build_tile_counts(concealedTiles)
    
    for i in range(34):
        if counts[i] >= 2:
            counts[i] -= 2
            if can_form_partial_melds(counts, totalMeldsNeededFromHand):
                counts[i] += 2
                return True
            counts[i] += 2
                
    return False

def is_standard_win(hand):
    if len(hand) != 14:
        return False
        
    counts = build_tile_counts(hand)
        
    for i in range(34):
        if counts[i] >= 2:
            counts[i] -= 2
            if can_form_melds(counts):
                counts[i] += 2
                return True

    return False

def hand_has_triplet(hand, tile):
    return hand.count(tile) >= 3

def is_honor(tile):
    return tile in HonorOrder

def is_terminal(tile):
    if tile in HonorOrder:
        return False
    return tile[0] == '1' or tile[0] == '9'

def is_terminal_or_honor(tile):
    return is_honor(tile) or is_terminal(tile)

def is_simple_tile(tile):
    return is_terminal_or_honor(tile) == False

def get_tile_suit(tile):
    if tile in HonorOrder:
        return None
    return tile[1]

def get_tile_number(tile):
    if tile in HonorOrder:
        return None
    return int(tile[0])

def get_player_hand_tiles(playerIndex):
    if playerIndex == app.mainPlayerIndex:
        return app.hand[:]
    return app.players[playerIndex]['hand'][:]

def get_player_last_drawn_tile(playerIndex):
    if playerIndex == app.mainPlayerIndex and app.drawnTile != None:
        return app.drawnTile
    return app.players[playerIndex].get('lastDrawnTile')

def get_player_seat_wind(playerIndex):
    return WindOrder[(playerIndex - app.dealerIndex) % 4]

def get_player_display_name(playerIndex):
    if playerIndex == app.mainPlayerIndex:
        return 'You'
    if playerIndex == 1:
        return 'Left AI'
    if playerIndex == 2:
        return 'Top AI'
    if playerIndex == 3:
        return 'Right AI'
    return 'Player ' + str(playerIndex + 1)

def get_hand_closed_state(playerIndex):
    for call in app.players[playerIndex]['calls']:
        if call['from'] != -1:
            return False
    return True

def player_hand_is_closed(playerIndex):
    return get_hand_closed_state(playerIndex)

def get_call_melds(playerIndex):
    melds = []
    for call in app.players[playerIndex]['calls']:
        meldType = 'sequence'
        if call['type'] == 'Pon':
            meldType = 'triplet'
        elif call['type'] == 'Kan':
            meldType = 'kan'

        melds.append({
            'type': meldType,
            'tiles': call['tiles'][:],
            'open': call['from'] != -1,
            'fromCall': True
        })
    return melds

def get_default_winning_tile(winType, playerIndex, winningTile=None):
    if winningTile != None:
        return winningTile

    if winType == 'tsumo':
        return get_player_last_drawn_tile(playerIndex)
    if winType == 'ron':
        return app.lastDiscardedTile

    return None

def get_all_tiles_for_yaku_check(winType, playerIndex=0, winningTile=None):
    fullHand = get_player_hand_tiles(playerIndex)

    winningTile = get_default_winning_tile(winType, playerIndex, winningTile)

    if winningTile != None:
        fullHand.append(winningTile)

    for call in app.players[playerIndex]['calls']:
        for tile in call['tiles']:
            fullHand.append(tile)

    return fullHand

def get_concealed_tiles_for_scoring(winType, playerIndex=0, winningTile=None):
    concealedTiles = get_player_hand_tiles(playerIndex)

    winningTile = get_default_winning_tile(winType, playerIndex, winningTile)

    if winningTile != None:
        concealedTiles.append(winningTile)

    return concealedTiles

def get_meld_base_tile(meld):
    tiles = meld['tiles'][:]
    sort_hand(tiles)
    return tiles[0]

def count_tile_occurrences(tiles):
    tileCounts = {}
    for tile in tiles:
        tileCounts[tile] = tileCounts.get(tile, 0) + 1
    return tileCounts

def build_standard_decompositions_from_counts(counts, meldsNeeded, currentMelds, pairTile, results):
    firstIndex = -1
    for i in range(34):
        if counts[i] > 0:
            firstIndex = i
            break

    if firstIndex == -1:
        if len(currentMelds) == meldsNeeded:
            results.append({'pairTile': pairTile, 'melds': currentMelds[:]})
        return

    if len(currentMelds) >= meldsNeeded:
        return

    tile = TileNamesByIndex[firstIndex]

    if counts[firstIndex] >= 3:
        counts[firstIndex] -= 3
        currentMelds.append({
            'type': 'triplet',
            'tiles': [tile, tile, tile],
            'open': False,
            'fromCall': False
        })
        build_standard_decompositions_from_counts(counts, meldsNeeded, currentMelds, pairTile, results)
        currentMelds.pop()
        counts[firstIndex] += 3

    if firstIndex <= 26:
        suitStart = (firstIndex // 9) * 9
        suitOffset = firstIndex - suitStart
        if suitOffset <= 6 and counts[firstIndex + 1] > 0 and counts[firstIndex + 2] > 0:
            tile2 = TileNamesByIndex[firstIndex + 1]
            tile3 = TileNamesByIndex[firstIndex + 2]
            counts[firstIndex] -= 1
            counts[firstIndex + 1] -= 1
            counts[firstIndex + 2] -= 1
            currentMelds.append({
                'type': 'sequence',
                'tiles': [tile, tile2, tile3],
                'open': False,
                'fromCall': False
            })
            build_standard_decompositions_from_counts(counts, meldsNeeded, currentMelds, pairTile, results)
            currentMelds.pop()
            counts[firstIndex] += 1
            counts[firstIndex + 1] += 1
            counts[firstIndex + 2] += 1

def get_standard_hand_decompositions(concealedTiles, playerIndex=0):
    meldsNeeded = 4 - len(app.players[playerIndex]['calls'])
    expectedTileCount = meldsNeeded * 3 + 2
    if len(concealedTiles) != expectedTileCount:
        return []

    counts = build_tile_counts(concealedTiles)
    results = []

    for i in range(34):
        if counts[i] >= 2:
            counts[i] -= 2
            build_standard_decompositions_from_counts(counts, meldsNeeded, [], TileNamesByIndex[i], results)
            counts[i] += 2

    return results

def meld_contains_terminal_or_honor(meld):
    for tile in meld['tiles']:
        if is_terminal_or_honor(tile):
            return True
    return False

def meld_is_terminal_sequence(meld):
    if meld['type'] != 'sequence':
        return False
    numbers = [get_tile_number(tile) for tile in meld['tiles']]
    return min(numbers) == 1 or max(numbers) == 9

def is_value_pair(tile, seatWind, roundWind):
    if tile in DragonTiles:
        return True
    if tile == seatWind:
        return True
    if tile == roundWind:
        return True
    return False

def get_wait_fu(standardResult, winningTile):
    if winningTile == None:
        return 0

    possibleFu = [0]

    if standardResult['pairTile'] == winningTile:
        possibleFu.append(2)

    for meld in standardResult['melds']:
        if meld['type'] != 'sequence':
            continue
        if meld['tiles'].count(winningTile) == 0:
            continue

        numbers = [get_tile_number(tile) for tile in meld['tiles']]
        smallest = min(numbers)
        if numbers[1] == get_tile_number(winningTile):
            possibleFu.append(2)
        elif smallest == 1 and get_tile_number(winningTile) == 3:
            possibleFu.append(2)
        elif smallest == 7 and get_tile_number(winningTile) == 7:
            possibleFu.append(2)
        else:
            possibleFu.append(0)

    return max(possibleFu)

def is_all_simples(tiles):
    for tile in tiles:
        if is_simple_tile(tile) == False:
            return False
    return True

def is_half_flush(tiles):
    suits = set()
    hasHonor = False
    for tile in tiles:
        if is_honor(tile):
            hasHonor = True
        else:
            suits.add(get_tile_suit(tile))
    return len(suits) == 1 and hasHonor

def is_full_flush(tiles):
    suits = set()
    for tile in tiles:
        if is_honor(tile):
            return False
        suits.add(get_tile_suit(tile))
    return len(suits) == 1

def is_all_honors(tiles):
    for tile in tiles:
        if is_honor(tile) == False:
            return False
    return True

def is_all_terminals(tiles):
    for tile in tiles:
        if is_terminal(tile) == False:
            return False
    return True

def is_all_green(tiles):
    for tile in tiles:
        if tile not in GreenTiles:
            return False
    return True

def is_nine_gates(tiles):
    if len(tiles) != 14:
        return False
    if is_full_flush(tiles) == False:
        return False

    suit = get_tile_suit(tiles[0])
    countsByNumber = {i: 0 for i in range(1, 10)}
    for tile in tiles:
        if get_tile_suit(tile) != suit:
            return False
        countsByNumber[get_tile_number(tile)] += 1

    if countsByNumber[1] < 3 or countsByNumber[9] < 3:
        return False
    for number in range(2, 9):
        if countsByNumber[number] < 1:
            return False

    return True

def count_dora(tiles):
    doraCount = 0
    doraTiles = get_dora_tiles_for_scoring()
    for tile in tiles:
        for doraTile in doraTiles:
            if tile == doraTile:
                doraCount += 1
    return doraCount

def add_yaku(yakuList, hanValue, label):
    yakuList.append({'name': label, 'han': hanValue})

def get_sequence_pattern_counts(melds):
    patternCounts = {}
    for meld in melds:
        if meld['type'] != 'sequence':
            continue
        pattern = meld['tiles'][0]
        patternCounts[pattern] = patternCounts.get(pattern, 0) + 1
    return patternCounts

def get_triplet_like_tiles(melds):
    tiles = []
    for meld in melds:
        if meld['type'] == 'triplet' or meld['type'] == 'kan':
            tiles.append(get_meld_base_tile(meld))
    return tiles

def winning_tile_completes_triplet_on_ron(scoreContext, standardResult):
    if scoreContext['winType'] != 'ron' or scoreContext['winningTile'] == None or standardResult == None:
        return False

    if standardResult['pairTile'] == scoreContext['winningTile']:
        return False

    for meld in standardResult['melds']:
        if meld['type'] == 'sequence' and scoreContext['winningTile'] in meld['tiles']:
            return False

    for meld in standardResult['melds']:
        if (meld['type'] == 'triplet' or meld['type'] == 'kan') and scoreContext['winningTile'] in meld['tiles']:
            return True

    return False

def count_concealed_triplets(scoreContext, standardResult):
    concealedTriplets = 0

    for meld in standardResult['melds']:
        if meld['type'] == 'triplet' or meld['type'] == 'kan':
            concealedTriplets += 1

    for meld in scoreContext['callMelds']:
        if meld['type'] == 'kan' and meld['open'] == False:
            concealedTriplets += 1

    if winning_tile_completes_triplet_on_ron(scoreContext, standardResult):
        concealedTriplets -= 1

    return concealedTriplets

def evaluate_yakuman(scoreContext, standardResult):
    fullTiles = scoreContext['fullTiles']
    allMelds = scoreContext['callMelds'][:]
    if standardResult != None:
        allMelds += standardResult['melds']

    yakumanList = []
    tripletTiles = get_triplet_like_tiles(allMelds)

    if is_thirteen_orphans(fullTiles):
        yakumanList.append('Thirteen Orphans')

    if is_all_honors(fullTiles):
        yakumanList.append('All Honors')

    if is_all_terminals(fullTiles):
        yakumanList.append('All Terminals')

    if is_all_green(fullTiles):
        yakumanList.append('All Green')

    dragonTriplets = 0
    for dragonTile in DragonTiles:
        if dragonTile in tripletTiles:
            dragonTriplets += 1
    if dragonTriplets == 3:
        yakumanList.append('Big Three Dragons')

    windTriplets = 0
    windPairCount = 0
    for windTile in WindOrder:
        if windTile in tripletTiles:
            windTriplets += 1
        elif standardResult != None and standardResult['pairTile'] == windTile:
            windPairCount += 1
    if windTriplets == 4:
        yakumanList.append('Big Four Winds')
    elif windTriplets == 3 and windPairCount == 1:
        yakumanList.append('Little Four Winds')

    if len([meld for meld in allMelds if meld['type'] == 'kan']) == 4:
        yakumanList.append('Four Kans')

    if standardResult != None:
        concealedTriplets = count_concealed_triplets(scoreContext, standardResult)
        if concealedTriplets >= 4 and scoreContext['isClosed']:
            if scoreContext['winType'] == 'tsumo' or standardResult['pairTile'] == scoreContext['winningTile']:
                yakumanList.append('Four Concealed Triplets')

    if scoreContext['isClosed'] and is_nine_gates(scoreContext['concealedTiles']):
        yakumanList.append('Nine Gates')

    return yakumanList

def evaluate_standard_yaku(scoreContext, standardResult):
    yakuList = []
    fullTiles = scoreContext['fullTiles']
    seatWind = scoreContext['seatWind']
    roundWind = scoreContext['roundWind']
    allMelds = scoreContext['callMelds'][:] + standardResult['melds']
    concealedSequences = [meld for meld in standardResult['melds'] if meld['type'] == 'sequence']
    sequencePatternCounts = get_sequence_pattern_counts(concealedSequences)
    tripletTiles = get_triplet_like_tiles(allMelds)
    waitFu = get_wait_fu(standardResult, scoreContext['winningTile'])

    if scoreContext['player']['riichiDeclared'] and scoreContext['isClosed']:
        add_yaku(yakuList, 1, 'Riichi')

    if scoreContext['isClosed'] and scoreContext['winType'] == 'tsumo':
        add_yaku(yakuList, 1, 'Menzen Tsumo')

    if is_all_simples(fullTiles) and (scoreContext['isClosed'] or app.openTanyaoEnabled):
        add_yaku(yakuList, 1, 'Tanyao')

    duplicateSequencePairs = 0
    for pattern, count in sequencePatternCounts.items():
        duplicateSequencePairs += count // 2
    if scoreContext['isClosed']:
        if duplicateSequencePairs >= 2:
            add_yaku(yakuList, 3, 'Ryanpeikou')
        elif duplicateSequencePairs >= 1:
            add_yaku(yakuList, 1, 'Iipeikou')

    if len([meld for meld in allMelds if meld['type'] != 'sequence']) == 0:
        pairTile = standardResult['pairTile']
        if is_value_pair(pairTile, seatWind, roundWind) == False and waitFu == 0 and scoreContext['isClosed']:
            add_yaku(yakuList, 1, 'Pinfu')

    for dragonTile in DragonTiles:
        if dragonTile in tripletTiles:
            if dragonTile == 'Wh':
                add_yaku(yakuList, 1, 'White Dragon')
            elif dragonTile == 'G':
                add_yaku(yakuList, 1, 'Green Dragon')
            elif dragonTile == 'R':
                add_yaku(yakuList, 1, 'Red Dragon')

    if seatWind in tripletTiles:
        add_yaku(yakuList, 1, 'Seat Wind')
    if roundWind in tripletTiles:
        add_yaku(yakuList, 1, 'Round Wind')

    sequenceStartsBySuit = {'m': set(), 'p': set(), 's': set()}
    for meld in allMelds:
        if meld['type'] != 'sequence':
            continue
        tile = meld['tiles'][0]
        sequenceStartsBySuit[get_tile_suit(tile)].add(get_tile_number(tile))

    for suit in ['m', 'p', 's']:
        if 1 in sequenceStartsBySuit[suit] and 4 in sequenceStartsBySuit[suit] and 7 in sequenceStartsBySuit[suit]:
            add_yaku(yakuList, 2 if scoreContext['isClosed'] else 1, 'Ittsu')
            break

    for start in range(1, 8):
        if start in sequenceStartsBySuit['m'] and start in sequenceStartsBySuit['p'] and start in sequenceStartsBySuit['s']:
            add_yaku(yakuList, 2 if scoreContext['isClosed'] else 1, 'Sanshoku Doujun')
            break

    if len([meld for meld in allMelds if meld['type'] == 'sequence']) == 0:
        add_yaku(yakuList, 2, 'Toitoi')

    concealedTriplets = count_concealed_triplets(scoreContext, standardResult)
    if concealedTriplets >= 3:
        add_yaku(yakuList, 2, 'Sanankou')

    if len([meld for meld in allMelds if meld['type'] == 'kan']) >= 3:
        add_yaku(yakuList, 2, 'Sankantsu')

    everySetHasTerminalOrHonor = meld_contains_terminal_or_honor({'tiles': [standardResult['pairTile'], standardResult['pairTile']], 'type': 'pair'})
    hasSequence = False
    hasHonor = is_honor(standardResult['pairTile'])
    junchanValid = is_terminal(standardResult['pairTile'])
    for meld in allMelds:
        if meld_contains_terminal_or_honor(meld) == False:
            everySetHasTerminalOrHonor = False
        if meld['type'] == 'sequence':
            hasSequence = True
            if meld_is_terminal_sequence(meld) == False:
                junchanValid = False
        elif meld_contains_terminal_or_honor(meld) == False:
            junchanValid = False
        for tile in meld['tiles']:
            if is_honor(tile):
                hasHonor = True
            if is_terminal(tile) == False:
                if is_honor(tile) == False:
                    junchanValid = False
    if everySetHasTerminalOrHonor and hasSequence:
        if junchanValid and hasHonor == False:
            add_yaku(yakuList, 3 if scoreContext['isClosed'] else 2, 'Junchan')
        else:
            add_yaku(yakuList, 2 if scoreContext['isClosed'] else 1, 'Chanta')

    if all(is_terminal_or_honor(tile) for tile in fullTiles):
        add_yaku(yakuList, 2, 'Honroutou')

    dragonTriplets = 0
    for dragonTile in DragonTiles:
        if dragonTile in tripletTiles:
            dragonTriplets += 1
    if dragonTriplets == 2 and standardResult['pairTile'] in DragonTiles:
        add_yaku(yakuList, 2, 'Shousangen')

    if is_half_flush(fullTiles):
        add_yaku(yakuList, 3 if scoreContext['isClosed'] else 2, 'Honitsu')
    elif is_full_flush(fullTiles):
        add_yaku(yakuList, 6 if scoreContext['isClosed'] else 5, 'Chinitsu')

    return yakuList

def calculate_standard_fu(scoreContext, standardResult, yakuList):
    pairTile = standardResult['pairTile']
    seatWind = scoreContext['seatWind']
    roundWind = scoreContext['roundWind']
    allMelds = scoreContext['callMelds'][:] + standardResult['melds']
    waitFu = get_wait_fu(standardResult, scoreContext['winningTile'])
    hasPinfu = False
    for yaku in yakuList:
        if yaku['name'] == 'Pinfu':
            hasPinfu = True
            break

    if hasPinfu and scoreContext['winType'] == 'tsumo':
        return 20

    fu = 20

    if scoreContext['winType'] == 'ron' and scoreContext['isClosed']:
        fu += 10
    elif scoreContext['winType'] == 'tsumo':
        fu += 2

    if pairTile in DragonTiles:
        fu += 2
    if pairTile == seatWind:
        fu += 2
    if pairTile == roundWind:
        fu += 2

    fu += waitFu

    for meld in allMelds:
        baseTile = meld['tiles'][0]
        isTerminalMeld = is_terminal_or_honor(baseTile)

        if meld['type'] == 'triplet':
            if meld['open']:
                fu += 4 if isTerminalMeld else 2
            else:
                fu += 8 if isTerminalMeld else 4
        elif meld['type'] == 'kan':
            if meld['open']:
                fu += 16 if isTerminalMeld else 8
            else:
                fu += 32 if isTerminalMeld else 16

    if fu == 20 and scoreContext['winType'] == 'ron' and scoreContext['isClosed'] == False:
        fu = 30

    if fu % 10 != 0:
        fu = ((fu // 10) + 1) * 10

    return fu

def calculate_payment_breakdown(basePoints, winType, isDealer):
    if winType == 'ron':
        multiplier = 6 if isDealer else 4
        points = ((basePoints * multiplier + 99) // 100) * 100
        return {'ron': points, 'total': points}

    if isDealer:
        eachPayment = ((basePoints * 2 + 99) // 100) * 100
        return {
            'dealerPays': eachPayment,
            'nonDealerPays': eachPayment,
            'total': eachPayment * 3
        }

    dealerPays = ((basePoints * 2 + 99) // 100) * 100
    nonDealerPays = ((basePoints + 99) // 100) * 100
    return {
        'dealerPays': dealerPays,
        'nonDealerPays': nonDealerPays,
        'total': dealerPays + nonDealerPays * 2
    }

def get_limit_base_points(han, fu):
    if han >= 13 and app.kazoeYakumanEnabled:
        return 8000, 'Kazoe Yakuman'
    if han >= 11:
        return 6000, 'Sanbaiman'
    if han >= 8:
        return 4000, 'Baiman'
    if han >= 6:
        return 3000, 'Haneman'
    if han >= 5 or (han == 4 and fu >= 40) or (han == 3 and fu >= 70):
        return 2000, 'Mangan'
    return None, None

def build_score_details(scoreContext, yakuList, fu, includeDora):
    normalHan = 0
    for yaku in yakuList:
        normalHan += yaku['han']

    doraCount = count_dora(scoreContext['fullTiles']) if includeDora else 0
    totalHan = normalHan + doraCount

    if normalHan == 0:
        return {
            'isValid': False,
            'han': 0,
            'fu': fu,
            'yaku': yakuList,
            'doraCount': doraCount,
            'yakuman': [],
            'payments': None,
            'limitName': None,
            'totalPoints': 0
        }

    basePoints, limitName = get_limit_base_points(totalHan, fu)
    if basePoints == None:
        basePoints = fu * (2 ** (totalHan + 2))

    payments = calculate_payment_breakdown(basePoints, scoreContext['winType'], scoreContext['isDealer'])
    return {
        'isValid': True,
        'han': totalHan,
        'fu': fu,
        'yaku': yakuList,
        'doraCount': doraCount,
        'yakuman': [],
        'payments': payments,
        'limitName': limitName,
        'totalPoints': payments['total']
    }

def build_yakuman_score_details(scoreContext, yakumanList):
    yakumanCount = len(yakumanList)
    basePoints = 8000 * yakumanCount
    payments = calculate_payment_breakdown(basePoints, scoreContext['winType'], scoreContext['isDealer'])
    return {
        'isValid': True,
        'han': None,
        'fu': None,
        'yaku': [],
        'doraCount': 0,
        'yakuman': yakumanList,
        'yakumanCount': yakumanCount,
        'payments': payments,
        'limitName': 'Yakuman' if yakumanCount == 1 else str(yakumanCount) + 'x Yakuman',
        'totalPoints': payments['total']
    }

def get_score_context(winType, playerIndex=0, winningTile=None):
    winningTile = get_default_winning_tile(winType, playerIndex, winningTile)

    concealedTiles = get_concealed_tiles_for_scoring(winType, playerIndex, winningTile)
    return {
        'playerIndex': playerIndex,
        'player': app.players[playerIndex],
        'winType': winType,
        'winningTile': winningTile,
        'concealedTiles': concealedTiles,
        'callMelds': get_call_melds(playerIndex),
        'fullTiles': get_all_tiles_for_yaku_check(winType, playerIndex, winningTile),
        'seatWind': get_player_seat_wind(playerIndex),
        'roundWind': app.roundWind,
        'isDealer': playerIndex == app.dealerIndex,
        'isClosed': get_hand_closed_state(playerIndex)
    }

def get_hand_yaku_and_score(winType, playerIndex=0, winningTile=None, includeDora=False):
    scoreContext = get_score_context(winType, playerIndex, winningTile)

    if is_valid_win_hand(scoreContext['concealedTiles'], playerIndex) == False:
        return {
            'isValid': False,
            'han': 0,
            'fu': 0,
            'yaku': [],
            'doraCount': 0,
            'yakuman': [],
            'payments': None,
            'limitName': None,
            'totalPoints': 0,
            'playerIndex': playerIndex,
            'winType': winType
        }

    specialYakuman = evaluate_yakuman(scoreContext, None)
    if len(specialYakuman) > 0:
        scoreDetails = build_yakuman_score_details(scoreContext, specialYakuman)
        scoreDetails['playerIndex'] = playerIndex
        scoreDetails['winType'] = winType
        return scoreDetails

    if is_seven_pairs(scoreContext['concealedTiles']):
        yakuList = []
        if scoreContext['player']['riichiDeclared'] and scoreContext['isClosed']:
            add_yaku(yakuList, 1, 'Riichi')
        if scoreContext['isClosed'] and winType == 'tsumo':
            add_yaku(yakuList, 1, 'Menzen Tsumo')
        add_yaku(yakuList, 2, 'Seven Pairs')
        if is_all_simples(scoreContext['fullTiles']) and (scoreContext['isClosed'] or app.openTanyaoEnabled):
            add_yaku(yakuList, 1, 'Tanyao')
        if all(is_terminal_or_honor(tile) for tile in scoreContext['fullTiles']):
            add_yaku(yakuList, 2, 'Honroutou')
        if is_half_flush(scoreContext['fullTiles']):
            add_yaku(yakuList, 3 if scoreContext['isClosed'] else 2, 'Honitsu')
        elif is_full_flush(scoreContext['fullTiles']):
            add_yaku(yakuList, 6 if scoreContext['isClosed'] else 5, 'Chinitsu')
        scoreDetails = build_score_details(scoreContext, yakuList, 25, includeDora)
        scoreDetails['playerIndex'] = playerIndex
        scoreDetails['winType'] = winType
        return scoreDetails

    standardResults = get_standard_hand_decompositions(scoreContext['concealedTiles'], playerIndex)
    bestScoreDetails = None

    for standardResult in standardResults:
        yakumanList = evaluate_yakuman(scoreContext, standardResult)
        if len(yakumanList) > 0:
            scoreDetails = build_yakuman_score_details(scoreContext, yakumanList)
        else:
            yakuList = evaluate_standard_yaku(scoreContext, standardResult)
            fu = calculate_standard_fu(scoreContext, standardResult, yakuList)
            scoreDetails = build_score_details(scoreContext, yakuList, fu, includeDora)

        scoreDetails['playerIndex'] = playerIndex
        scoreDetails['winType'] = winType

        if bestScoreDetails == None or scoreDetails['totalPoints'] > bestScoreDetails['totalPoints']:
            bestScoreDetails = scoreDetails
        elif scoreDetails['totalPoints'] == bestScoreDetails['totalPoints']:
            currentHan = -1 if scoreDetails['han'] == None else scoreDetails['han']
            bestHan = -1 if bestScoreDetails['han'] == None else bestScoreDetails['han']
            if currentHan > bestHan:
                bestScoreDetails = scoreDetails
            elif currentHan == bestHan and scoreDetails['fu'] != None and bestScoreDetails['fu'] != None and scoreDetails['fu'] > bestScoreDetails['fu']:
                bestScoreDetails = scoreDetails

    if bestScoreDetails == None:
        return {
            'isValid': False,
            'han': 0,
            'fu': 0,
            'yaku': [],
            'doraCount': 0,
            'yakuman': [],
            'payments': None,
            'limitName': None,
            'totalPoints': 0,
            'playerIndex': playerIndex,
            'winType': winType
        }

    return bestScoreDetails

def format_score_text(scoreDetails):
    if scoreDetails['isValid'] == False:
        return 'No scoring yaku'

    if len(scoreDetails['yakuman']) > 0:
        return str(scoreDetails['totalPoints']) + ' points'

    payments = scoreDetails['payments']
    scoreText = str(scoreDetails['totalPoints']) + ' points'

    if 'ron' in payments:
        scoreText += ' (' + str(payments['ron']) + ' ron)'
    else:
        scoreText += ' (' + str(payments['nonDealerPays']) + '/' + str(payments['dealerPays']) + ' tsumo)'

    return scoreText

def format_yaku_lines(scoreDetails):
    if scoreDetails['isValid'] == False:
        return ['No scoring yaku']

    if len(scoreDetails['yakuman']) > 0:
        yakuLines = [scoreDetails['limitName']]
        for yakumanName in scoreDetails['yakuman']:
            yakuLines.append(yakumanName)
        return yakuLines

    yakuLines = [str(scoreDetails['han']) + ' han, ' + str(scoreDetails['fu']) + ' fu']

    if scoreDetails['limitName'] != None:
        yakuLines.append(scoreDetails['limitName'])

    for yaku in scoreDetails['yaku']:
        yakuLines.append(yaku['name'] + ' (' + str(yaku['han']) + ')')

    if scoreDetails['doraCount'] > 0:
        yakuLines.append('Dora (' + str(scoreDetails['doraCount']) + ')')

    return yakuLines

def has_player_yaku(winType, playerIndex=0, winningTile=None):
    scoreDetails = get_hand_yaku_and_score(winType, playerIndex, winningTile, includeDora=False)
    return scoreDetails['isValid']

def update_player_action_prompt():
    app.actionOptions = []
    app.actionPromptOpen = False
    
    if app.currentPlayer != 0:
        return
    
    fullHand = app.hand[:]
    if app.drawnTile != None:
        fullHand.append(app.drawnTile)
    
    # Check for closed kan first
    closedKanTiles = get_player_closed_kan_tiles()
    if len(closedKanTiles) > 0:
        for tile in closedKanTiles:
            app.actionOptions.append('Kan ' + tile)
        app.actionOptions.append('Pass')
        app.actionPromptOpen = True
        return
        
    if is_valid_win_hand(fullHand) and has_player_yaku('tsumo'):
        app.actionOptions = ['Tsumo', 'Pass']
        app.actionPromptOpen = True
        return

    if player_hand_is_closed(app.mainPlayerIndex) and app.players[0]['riichiDeclared'] == False and hand_is_tenpai_for_riichi(fullHand):
        app.actionOptions = ['Riichi', 'Pass']
        app.actionPromptOpen = True

def update_player_ron_prompt():
    app.actionOptions = []
    app.actionPromptOpen = False
    
    if app.lastDiscardedTile == None:
        return
    
    fullHand = app.hand[:]
    fullHand.append(app.lastDiscardedTile)
    
    if is_valid_win_hand(fullHand) and has_player_yaku('ron'):
        app.actionOptions = ['Ron', 'Pass']
        app.actionPromptOpen = True

def show_player_discard_call_options(options):
    app.actionOptions = options[:]
    if 'Pass' not in app.actionOptions:
        app.actionOptions.append('Pass')
    app.actionPromptOpen = True
        
        
def chi_option_to_text(chiTiles, claimedTile):
    fullTiles = chiTiles[:] + [claimedTile]
    sort_hand(fullTiles)
    return 'Chi ' + '-'.join(fullTiles)
    
def show_player_chi_choice_prompt():
    app.actionOptions = []
    app.actionPromptOpen = True
    
    for chiTiles in app.pendingChiOptions:
        app.actionOptions.append(chi_option_to_text(chiTiles, app.pendingCallTile))
        

def get_action_button_width(action):
    if action.startswith('Chi '):
        return 80
    if action.startswith('Kan '):
        return 50
    return 50
        
def get_centered_action_buttons_start_x(actions, gap):
    totalWidth = 0
    
    for i in range(len(actions)):
        totalWidth += get_action_button_width(actions[i])
        
    totalWidth += gap * (len(actions) - 1)
        
    return (400 - totalWidth) / 2

def draw_action_buttons():
    app.actionButtonTargets = []
    
    if app.actionPromptOpen == False:
        return
    
    y = 300
    gap = 8
    x = get_centered_action_buttons_start_x(app.actionOptions, gap)
    
    for i in range(len(app.actionOptions)):
        action = app.actionOptions[i]
        
        color = 'gray'
        textColor = 'white'
        buttonWidth = get_action_button_width(action)
        
        
        if action.startswith('Chi '):
            color = 'lightGreen'
            textColor = 'black'
        elif action.startswith('Kan '):
            color = 'mediumpurple'
            textColor = 'white'
        elif action == 'Tsumo':
            color = 'crimson'
            textColor = 'white'
        elif action == 'Ron':
            color = 'red'
            textColor = 'white'
        elif action == 'Pon':
            color = 'blue'
            textColor = 'white'
        elif action == 'Chi':
            color = 'lightGreen'
            textColor = 'white'
        elif action == 'Kan':
            color = 'mediumpurple'
            textColor = 'white'
        elif action == 'Riichi':
            color = 'orange'
            textColor = 'white'
        elif action == 'Pass':
            color = 'gray'
            textColor = 'white'
                
        app.scene.add(Rect(x, y, buttonWidth, 32, fill=color, border='white', borderWidth=1))
        app.scene.add(Label(action, x + buttonWidth / 2, y + 16, size=9, fill=textColor, bold=True))
        
        app.actionButtonTargets.append({
            'type': 'actionButton',
            'action': action,
            'x': x,
            'y': y,
            'w': buttonWidth,
            'h': 32
            })
            
        x += buttonWidth + gap
    
    
def get_menzenchin_text(playerIndex):
    if player_hand_is_closed(playerIndex):
        return 'Menzenchin'
    return 'Open Hand'

def start_new_hand():
    reset_round_state()
    app.players, app.wall = deal_starting_hands()
    app.hand = app.players[app.mainPlayerIndex]['hand']
    initialize_dora_state()
    
    app.TotalHandWidth = len(app.hand) * TileWidth + (len(app.hand) - 1) * TileGap
    app.HandX = (400 - app.TotalHandWidth) / 2
    
    redraw_game()

def start_with_custom_hand(playerHand):
    reset_round_state()
    
    # Create the wall without the player's hand
    newWall = build_wall()
    
    # Remove player's hand from wall
    playerHandCopy = playerHand[:]
    for tile in playerHandCopy:
        if tile in newWall:
            newWall.remove(tile)
    
    random.shuffle(newWall)
    
    # Deal hands for other players
    players = [
        {'hand': playerHand[:], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None},
        {'hand': [], 'discards': [], 'calls': [], 'riichiDeclared': False, 'lastDrawnTile': None}
    ]
    
    # Deal to other players
    for roundNumber in range(13):
        for playerIndex in range(1, 4):
            if len(newWall) > 0:
                players[playerIndex]['hand'].append(newWall.pop())
    
    # Player's hand is already set
    app.players = players
    app.wall = newWall
    app.hand = app.players[app.mainPlayerIndex]['hand']
    initialize_dora_state()
    
    app.TotalHandWidth = len(app.hand) * TileWidth + (len(app.hand) - 1) * TileGap
    app.HandX = (400 - app.TotalHandWidth) / 2
    
    app.currentScene = 'mahjong'
    redraw_game()

def draw_hand_select_scene():
    app.scene.clear()
    app.handSelectionButtonTargets = []
    
    app.scene.add(Rect(0, 0, 400, 400, fill=rgb(34, 120, 70)))
    app.scene.add(Label('Enter Your Starting Hand', 200, 25, size=18, fill='white', bold=True))
    
    # Instructions
    app.scene.add(Label('Format: E, E, E, 1m, 2p, 3s, ...', 200, 55, size=12, fill='lightBlue', bold=True))
    app.scene.add(Label('Need exactly 14 tiles, max 4 of each', 200, 75, size=11, fill='white'))
    
    # Input box
    inputBoxX = 30
    inputBoxY = 110
    inputBoxW = 340
    inputBoxH = 60
    
    app.scene.add(Rect(inputBoxX, inputBoxY, inputBoxW, inputBoxH, fill='white', border='lightBlue', borderWidth=2))
    
    # Display the input text
    displayText = app.customHandInput
    if len(displayText) > 60:
        displayText = displayText[:57] + '...'
    
    app.scene.add(Label(displayText, inputBoxX + 10, inputBoxY + 20, size=11, fill='black', align='left'))
    
    # Register input box as clickable
    app.handSelectionButtonTargets.append({
        'type': 'inputBox',
        'x': inputBoxX,
        'y': inputBoxY,
        'w': inputBoxW,
        'h': inputBoxH
    })
    
    # Error message
    if app.customHandError != '':
        app.scene.add(Label(app.customHandError, 200, 190, size=12, fill='red', bold=True))
    
    # Submit button
    submitX = 80
    submitY = 240
    submitW = 240
    submitH = 40
    
    app.scene.add(Rect(submitX, submitY, submitW, submitH, fill='lightGreen', border='white', borderWidth=2))
    app.scene.add(Label('Submit', 200, submitY + 20, size=14, fill='darkGreen', bold=True))
    
    app.handSelectionButtonTargets.append({
        'type': 'submit',
        'x': submitX,
        'y': submitY,
        'w': submitW,
        'h': submitH
    })
    
    # Clear button
    clearX = 80
    clearY = 300
    clearW = 240
    clearH = 40
    
    app.scene.add(Rect(clearX, clearY, clearW, clearH, fill='lightCoral', border='white', borderWidth=2))
    app.scene.add(Label('Clear', 200, clearY + 20, size=14, fill='darkRed', bold=True))
    
    app.handSelectionButtonTargets.append({
        'type': 'clear',
        'x': clearX,
        'y': clearY,
        'w': clearW,
        'h': clearH
    })
    
    app.scene.add(Label('Press ESC to go back', 200, 390, size=12, fill='white'))

def draw_round_result_overlay():
    app.resultButtonTarget = None
    
    if app.roundResult == None:
        return
    
    app.scene.add(Rect(0, 0, 400, 400, fill='black', opacity=55))
    
    if app.roundResult == 'win':
        app.scene.add(Label('YOU WIN', 200, 170, size=28, fill='gold', bold=True))
        app.scene.add(Label(app.roundResultReason, 200, 205, size=18, fill='white', bold=True))
        if app.roundScoreText != '':
            app.scene.add(Label(app.roundScoreText, 200, 232, size=12, fill='lightBlue', bold=True))
    elif app.roundResult == 'loss':
        app.scene.add(Label('YOU LOSE', 200, 170, size=28, fill='red', bold=True))
        app.scene.add(Label(app.roundResultReason, 200, 205, size=18, fill='white', bold=True))
        if app.roundScoreText != '':
            app.scene.add(Label(app.roundScoreText, 200, 232, size=12, fill='lightBlue', bold=True))

    if len(app.roundYakuLines) > 0:
        panelX = 272
        panelY = 132
        panelW = 118
        panelH = 132
        lineY = panelY + 28

        app.scene.add(Rect(panelX, panelY, panelW, panelH, fill=rgb(24, 40, 56), border='white', borderWidth=1, opacity=92))
        app.scene.add(Label('Yaku', panelX + panelW / 2, panelY + 13, size=12, fill='gold', bold=True))

        for i in range(min(len(app.roundYakuLines), 7)):
            app.scene.add(Label(app.roundYakuLines[i], panelX + 8, lineY + i * 14, size=9, fill='white', align='left'))
        
    buttonX = 145
    buttonY = 240
    buttonW = 110
    buttonH = 36
    
    app.scene.add(Rect(buttonX, buttonY, buttonW, buttonH, fill='lightBlue', border='white', borderWidth=2))
    app.scene.add(Label('New Hand', buttonX + buttonW / 2, buttonY + buttonH / 2, size=14, fill='darkBlue', bold=True))
    
    app.resultButtonTarget = {
        'x': buttonX,
        'y': buttonY,
        'w': buttonW,
        'h': buttonH
        }


def update_no_yaku_warning():
    app.noYakuWarning = ''

    if player_hand_is_closed(app.mainPlayerIndex):
        return

    seatWind = get_player_seat_wind(app.mainPlayerIndex)
    for meld in get_call_melds(app.mainPlayerIndex):
        if meld['type'] != 'triplet' and meld['type'] != 'kan':
            continue

        meldTile = get_meld_base_tile(meld)
        if meldTile in DragonTiles or meldTile == seatWind or meldTile == app.roundWind:
            return

    app.noYakuWarning = 'No Yaku'

def get_tutorial_page_count():
    return 4
    
    
def draw_tutorial_page_indicator():
    pageText = 'Page ' + str(app.tutorialPage + 1) + ' / ' + str(get_tutorial_page_count())
    app.scene.add(Label(pageText, 200, 30, size=16, fill='white', bold=True))
    
    
def draw_tutorial_page_1():
    app.scene.add(Label('How to Win', 200, 60, size=22, fill='gold', bold=True))
    app.scene.add(Label('Make 4 groups and 1 pair.', 200, 90, size=14, fill='white', bold=True))
    
    app.scene.add(Label('Examples of groups:', 200, 120, size=14, fill='lightBlue', bold=True))
    
    draw_mini_tile(90, 145, '3m')
    draw_mini_tile(112, 145, '4m')
    draw_mini_tile(134, 145, '5m')
    app.scene.add(Label('Sequence', 185, 160, size=13, fill='white'))
    
    draw_mini_tile(235, 145, '7p')
    draw_mini_tile(257, 145, '7p')
    draw_mini_tile(279, 145, '7p')
    app.scene.add(Label('Triplet', 320, 160, size=13, fill='white'))
    
    app.scene.add(Label('Example of a pair:', 200, 205, size=14, fill='lightBlue', bold=True))
    
    draw_mini_tile(160, 225, 'E')
    draw_mini_tile(182, 225, 'E')
    app.scene.add(Label('Pair', 230, 240, size=13, fill='white'))
    
    app.scene.add(Label('A complete winning hand uses 4 groups plus 1 pair.', 200, 290, size=13, fill='white'))
    
def draw_tutorial_page_2():
    app.scene.add(Label('Pon and Chi', 200, 60, size=22, fill='gold', bold=True))
    
    app.scene.add(Label("Pon: claim an opponent's discard to make a triplet.", 200, 100, size=14, fill='white'))
    draw_mini_tile(105, 130, '5p')
    draw_mini_tile(127, 130, '5p')
    app.scene.add(Label('+ discarded 5p = Pon', 245, 145, size=13, fill='lightBlue'))
    
    app.scene.add(Label("Chi: claim ONLY the previous player's discard", 200, 195, size=14, fill='white'))
    app.scene.add(Label('to make a sequence.', 200, 215, size=14, fill='white'))
    
    draw_mini_tile(95, 245, '4s')
    draw_mini_tile(117, 245, '5s')
    app.scene.add(Label('+ discarded 6s = Chi', 245, 260, size=13, fill='lightBlue'))
    
    app.scene.add(Label('After Pon or Chi, your hand becomes open.', 200, 310, size=13, fill='white'))
    app.scene.add(Label('Open hands need a yaku to win.', 200, 332, size=13, fill='orange', bold=True))
    
    
def draw_tutorial_page_3():
    app.scene.add(Label('Tsumo and Ron', 200, 60, size=22, fill='gold', bold=True))
    
    app.scene.add(Label('Tsumo = win on your own draw', 200, 100, size=14, fill='white'))
    app.scene.add(Label("Ron = win on another player's discard", 200, 128, size=14, fill='white'))
    
    app.scene.add(Label('A winning hand needs a yaku.', 200, 155, size=15, fill='lightBlue', bold=True))
    
    app.scene.add(Label('Yaku in this version:', 200, 185, size=14, fill='white', bold=True))
    app.scene.add(Label('Riichi, Tanyao, Pinfu, Iipeikou', 200, 208, size=13, fill='white'))
    app.scene.add(Label('Yakuhai, Toitoi, Sanshoku, Ittsu', 200, 228, size=13, fill='white'))
    app.scene.add(Label('Honitsu, Chinitsu, Chanta and more', 200, 248, size=13, fill='white'))
    
    app.scene.add(Label('Example yaku:', 200, 280, size=14, fill='lightBlue', bold=True))
    
    draw_mini_tile(92, 302, 'E')
    draw_mini_tile(114, 302, 'E')
    draw_mini_tile(136, 302, 'E')
    app.scene.add(Label('East triplet', 210, 317, size=13, fill='white'))
    
    draw_mini_tile(92, 328, 'R')
    draw_mini_tile(114, 328, 'R')
    draw_mini_tile(136, 328, 'R')
    app.scene.add(Label('Red dragon triplet', 228, 343, size=13, fill='white'))
    
    
def draw_tutorial_page_0():
    app.scene.add(Label('Controls', 200, 60, size=22, fill='gold', bold=True))
    
    app.scene.add(Label('Click a tile once to select it.', 200, 110, size=14, fill='white'))
    app.scene.add(Label('Click the selected tile again to discard it.', 200, 140, size=14, fill='white'))
    
    app.scene.add(Label('When action buttons appear:', 200, 200, size=14, fill='lightBlue', bold=True))
    app.scene.add(Label('- Pon claims a matching discard', 200, 230, size=13, fill='white'))
    app.scene.add(Label('- Chi claims a sequence from the previous player', 200, 255, size=13, fill='white'))
    app.scene.add(Label('- Ron wins on a discard', 200, 280, size=13, fill='white'))
    app.scene.add(Label('- Tsumo wins on your draw', 200, 305, size=13, fill='white'))
    
    app.scene.add(Label('Use the arrows to read the other tutorial pages.', 200, 345, size=13, fill='white'))

def draw_tutorial_overlay():
    app.tutorialButtonTargets = []
    
    if app.tutorialOpen == False:
        return
    
    app.scene.add(Rect(0, 0, 400, 400, fill='black', opacity=88))
    
    draw_tutorial_page_indicator()
    
    if app.tutorialPage == 0:
        draw_tutorial_page_0()
    elif app.tutorialPage == 1:
        draw_tutorial_page_1()
    elif app.tutorialPage == 2:
        draw_tutorial_page_2()
    elif app.tutorialPage == 3:
        draw_tutorial_page_3()
    
    # back button
    app.scene.add(Rect(150, 362, 100, 28, fill='lightCoral', border='white', borderWidth=2))
    app.scene.add(Label('Back', 200, 376, size=14, fill='white', bold=True))
    app.tutorialButtonTargets.append({
        'type': 'tutorialBack',
        'x': 150,
        'y': 362,
        'w': 100,
        'h': 28
            })
        
    # left arrow
    if app.tutorialPage > 0:
        app.scene.add(Rect(18, 180, 34, 40, fill='lightBlue', border='white', borderWidth=2))
        app.scene.add(Label('<', 35, 200, size=24, fill='darkBlue', bold=True))
        app.tutorialButtonTargets.append({
            'type': 'tutorialPrev',
            'x': 18,
            'y': 180,
            'w': 34,
            'h': 40
            })
    
    # right arrow
    if app.tutorialPage < get_tutorial_page_count() - 1:
        app.scene.add(Rect(348, 180, 34, 40, fill='lightBlue', border='white', borderWidth=2))
        app.scene.add(Label('>', 365, 200, size=24, fill='darkBlue', bold=True))
        app.tutorialButtonTargets.append({
            'type': 'tutorialNext',
            'x': 348,
            'y': 180,
            'w': 34,
            'h': 40
            })
        
def update_room_interaction_state():
    playerLeft = app.playerX - app.playerSize / 2
    playerRight = app.playerX + app.playerSize / 2
    playerTop = app.playerY - app.playerSize / 2
    playerBottom = app.playerY + app.playerSize / 2

    rangePadding = 20

    tableLeft = app.tableX - rangePadding
    tableRight = app.tableX + app.tableW + rangePadding
    tableTop = app.tableY - rangePadding
    tableBottom = app.tableY + app.tableH + rangePadding

    app.playerNearTable = (
        playerRight >= tableLeft and
        playerLeft <= tableRight and
        playerBottom >= tableTop and
        playerTop <= tableBottom
    )
    
    handSelectTableLeft = app.handSelectTableX - rangePadding
    handSelectTableRight = app.handSelectTableX + app.handSelectTableW + rangePadding
    handSelectTableTop = app.handSelectTableY - rangePadding
    handSelectTableBottom = app.handSelectTableY + app.handSelectTableH + rangePadding
    
    app.playerNearHandSelectTable = (
        playerRight >= handSelectTableLeft and
        playerLeft <= handSelectTableRight and
        playerBottom >= handSelectTableTop and
        playerTop <= handSelectTableBottom
    )

    tutorialNpcLeft = app.tutorialNpcX - app.tutorialNpcSize / 2 - rangePadding
    tutorialNpcRight = app.tutorialNpcX + app.tutorialNpcSize / 2 + rangePadding
    tutorialNpcTop = app.tutorialNpcY - app.tutorialNpcSize / 2 - rangePadding
    tutorialNpcBottom = app.tutorialNpcY + app.tutorialNpcSize / 2 + rangePadding

    app.playerNearTutorialNpc = (
        playerRight >= tutorialNpcLeft and
        playerLeft <= tutorialNpcRight and
        playerBottom >= tutorialNpcTop and
        playerTop <= tutorialNpcBottom
    )

def draw_room_scene():
    app.scene.add(Rect(0, 0, 400, 400, fill=rgb(84, 62, 44)))
    app.scene.add(Rect(20, 20, 360, 360, fill=rgb(132, 94, 66)))

    app.scene.add(Label('Mahjong Room', 200, 25, size=18, fill='white', bold=True))

    # main table
    app.scene.add(Rect(app.tableX, app.tableY, app.tableW, app.tableH,
                       fill=rgb(40, 120, 70), border='black', borderWidth=2))
    app.scene.add(Label('Random Hand',
                        app.tableX + app.tableW / 2,
                        app.tableY + app.tableH / 2,
                        size=12, fill='white', bold=True))
    
    # hand select table
    app.scene.add(Rect(app.handSelectTableX, app.handSelectTableY, app.handSelectTableW, app.handSelectTableH,
                       fill=rgb(40, 120, 70), border='black', borderWidth=2))
    app.scene.add(Label('Choose Hand',
                        app.handSelectTableX + app.handSelectTableW / 2,
                        app.handSelectTableY + app.handSelectTableH / 2,
                        size=12, fill='white', bold=True))

    # tutorial npc
    app.scene.add(Rect(app.tutorialNpcX - app.tutorialNpcSize / 2,
                       app.tutorialNpcY - app.tutorialNpcSize / 2,
                       app.tutorialNpcSize,
                       app.tutorialNpcSize,
                       fill='lightBlue', border='navy', borderWidth=2))
    app.scene.add(Label('?', app.tutorialNpcX, app.tutorialNpcY + 1, size=16, fill='navy', bold=True))

    app.scene.add(Rect(app.playerX - app.playerSize / 2,
                       app.playerY - app.playerSize / 2,
                       app.playerSize,
                       app.playerSize,
                       fill='gold', border='black'))

    app.scene.add(Label('Tutorial NPC', 55, 354, size=11, fill='white', bold=True))

    app.scene.add(Label('WASD to move', 75, 370, size=12, fill='white'))
    app.scene.add(Label('Walk to a table', 200, 370, size=12, fill='white'))

    if app.playerNearTable:
        app.scene.add(Label('Press E to play with random hand', 200, 90, size=14, fill='yellow', bold=True))
    
    if app.playerNearHandSelectTable:
        app.scene.add(Label('Press E to choose starting hand', 200, 90, size=14, fill='yellow', bold=True))

    if app.playerNearTutorialNpc:
        app.scene.add(Label('Press E to open tutorial', 200, 90, size=14, fill='yellow', bold=True))

def draw_mahjong_scene():
    app.scene.clear()
    app.clickTargets = []
    
    app.scene.add(Rect(0, 0, 400, 400, fill=rgb(34, 120, 70)))
    
    app.scene.add(Rect(110, 110, 180, 180, fill=rgb(45, 140, 85), border=rgb(20, 90, 50)))
    #app.scene.add(Label('Center Table Space', 200, 200, size=16, fill='white', bold=True))
    
    # discard history button ADD IN FUTURE
    #app.scene.add(Rect(10, 10, 60, 35, fill='lightBlue', border='blue', borderWidth=2))
    #app.scene.add(Label('Discards', 40, 27, size=12, fill='darkBlue', bold=True))
    
    app.scene.add(Label('Riichi Mahjong', 200, 25, size=18, fill='white', bold=True))
    draw_dora_indicator_panel()
    #app.scene.add(Label(f'Tile size: {TileWidth}x{TileHeight}', 200, 45, size=12, fill='white'))
    #app.scene.add(Label(f'Total hand width: {int(app.TotalHandWidth)} px', 200, 60, size=12, fill='white'))
    app.scene.add(Label(f'Wall tiles left: {len(app.wall)}', 200, 45, size=12, fill='white'))
    
    #Menzenchin checker
    #app.scene.add(Label(get_menzenchin_text(0), 200, 84, size=12, fill='white'))
    
    #app.scene.add(Label(f'Top AI tiles: {len(app.players[2]["hand"])}', 200, 95, size=12, fill='white'))
    #app.scene.add(Label(f'Left AI tiles: {len(app.players[1]["hand"])}', 60, 200, size=12, fill='white', rotateAngle=-90))
    #app.scene.add(Label(f'Right AI tiles: {len(app.players[3]["hand"])}', 340, 200, size=12, fill='white', rotateAngle=90))
    
    app.scene.add(Label('Top AI', 200, 95, size=12, fill='white'))
    app.scene.add(Label('Left AI', 60, 200, size=12, fill='white'))
    app.scene.add(Label('Right AI', 340, 200, size=12, fill='white'))
    
    
    if app.currentPlayer == 0:
        turnText = 'Turn: Player'
    elif app.currentPlayer == 1:
        turnText = 'Turn: Left AI'
    elif app.currentPlayer == 2:
        turnText = 'Turn: Top AI'
    else:
        turnText = 'Turn: Right AI'
    app.scene.add(Label(turnText, 200, 72, size=12, fill='white', bold=True))
                    
                    
    
    
    draw_recent_discards()
    draw_preview_panel()
    draw_action_buttons()
    draw_player_calls()
    
    if app.noYakuWarning != '':
        warningX = app.HandX + TileWidth / 2
        app.scene.add(Label(app.noYakuWarning, warningX, HandY - 22, size=12, fill='orange', bold=True))
    
    #app.scene.add(Rect(app.HandX - 4, HandY - 4, app.TotalHandWidth + 8, TileHeight + 8, fill=None, border='gold', borderWidth=1))
    app.scene.add(Label('Player Hand', 200, HandY - 12, size=12, fill='white', bold=True))

    legalRiichiDiscardIndices = []
    if app.players[0]['riichiDeclared']:
        legalRiichiDiscardIndices = get_riichi_legal_discard_indices()
        legalRiichiDiscardIndexSet = set(legalRiichiDiscardIndices)
    else:
        legalRiichiDiscardIndexSet = None
    
    for i in range(len(app.hand)):
        TileX = app.HandX + i * (TileWidth + TileGap)
        isLegalDiscard = True
        if legalRiichiDiscardIndexSet != None:
            isLegalDiscard = i in legalRiichiDiscardIndexSet

        draw_tile(TileX, HandY, app.hand[i], dimmed=isLegalDiscard == False)

        if isLegalDiscard:
            app.clickTargets.append({
                'type': 'hand',
                'index': i,
                'tile': app.hand[i],
                'x': TileX,
                'y': HandY,
                'w': TileWidth,
                'h': TileHeight
            })

        if app.selectedHandIndex == i:
            draw_selected_outline(TileX, HandY)
        
    if app.drawnTile != None:
        drawnTileX = app.HandX + len(app.hand) * (TileWidth + TileGap) + 12
        drawnTileIsLegal = True
        if legalRiichiDiscardIndexSet != None:
            drawnTileIsLegal = len(app.hand) in legalRiichiDiscardIndexSet

        draw_tile(drawnTileX, HandY, app.drawnTile, dimmed=drawnTileIsLegal == False)
        
        if drawnTileIsLegal:
            app.clickTargets.append({
                'type': 'drawnTile',
                'index': len(app.hand),
                'tile': app.drawnTile,
                'x': drawnTileX,
                'y': HandY,
                'w': TileWidth,
                'h': TileHeight
                })
            
    if app.selectedHandIndex == len(app.hand):
        draw_selected_outline(drawnTileX, HandY)
        

    if app.gameMessage != '':
        app.scene.add(Label(app.gameMessage, 200, 58, size=12, fill='gold', bold=True))
        
    draw_round_result_overlay()
    draw_tutorial_overlay()
    
def redraw_game():
    app.scene.clear()

    if app.currentScene == 'room':
        draw_room_scene()
    elif app.currentScene == 'mahjong':
        draw_mahjong_scene()
    elif app.currentScene == 'handSelect':
        draw_hand_select_scene()

def point_in_rect(mouseX, mouseY, rectX, rectY, rectW, rectH):
    return (
        mouseX >= rectX and
        mouseX <= rectX + rectW and
        mouseY >= rectY and
        mouseY <= rectY + rectH
        )
        
def draw_tile_for_player():
    # Add the currently drawn tile to hand if one exists
    if app.drawnTile is not None:
        app.hand.append(app.drawnTile)
        sort_hand(app.hand)
        app.players[app.mainPlayerIndex]['lastDrawnTile'] = None
    
    if len(app.wall) == 0:
        return
    
    app.drawnTile = app.wall.pop()
    app.players[app.mainPlayerIndex]['lastDrawnTile'] = app.drawnTile
    
def draw_tile_for_ai(playerIndex):
    if len(app.wall) == 0:
        return
    
    drawnTile = app.wall.pop()
    app.players[playerIndex]['hand'].append(drawnTile)
    app.players[playerIndex]['lastDrawnTile'] = drawnTile
    sort_hand(app.players[playerIndex]['hand'])
    
def ai_discard_random_tile(playerIndex):
    if len(app.players[playerIndex]['hand']) == 0:
        return
    
    randomIndex = random.randrange(len(app.players[playerIndex]['hand']))
    discardedTile = app.players[playerIndex]['hand'].pop(randomIndex)
    app.players[playerIndex]['discards'].append(discardedTile)
    app.lastDiscardedTile = discardedTile
    app.lastDiscarder = playerIndex
    app.previewTile = discardedTile
    app.players[playerIndex]['lastDrawnTile'] = None
    sort_hand(app.players[playerIndex]['hand'])
    
def start_ai_turns():
    app.pendingAiPlayers = [3, 2, 1]
    app.aiThinking = True
    app.aiDelayCounter = app.aiTurnDelay
    app.currentPlayer = 3
    
def discard_selected_tile():
    if app.selectedHandIndex == None:
        return

    if app.players[0]['riichiDeclared']:
        legalRiichiDiscardIndices = get_riichi_legal_discard_indices()
        if app.selectedHandIndex not in legalRiichiDiscardIndices:
            return
    
    if app.selectedHandIndex == len(app.hand) and app.drawnTile != None:
        discardedTile = app.drawnTile
        app.drawnTile = None
    else:
        discardedTile = app.hand.pop(app.selectedHandIndex)
    if app.drawnTile != None:
        app.hand.append(app.drawnTile)
        app.drawnTile = None
        sort_hand(app.hand)

    app.players[app.mainPlayerIndex]['lastDrawnTile'] = None
        
    app.players[0]['discards'].append(discardedTile)
    
    app.lastDiscardedTile = discardedTile
    app.lastDiscarder = 0
    app.selectedHandIndex = None
    app.previewTile = discardedTile
    
    app.gameMessage = ''
    app.actionPromptOpen = False
    app.actionOptions = []
    
    redraw_game()
    start_ai_turns()
    
def can_player_pon(tile):
    return app.hand.count(tile) >= 2
    
    
def can_player_kan_on_discard(tile):
    return app.hand.count(tile) >= 3


def get_player_closed_kan_tiles():
    kanTiles = []
    for tile in HonorOrder:
        if app.hand.count(tile) >= 4:
            kanTiles.append(tile)
    for suit in ['m', 'p', 's']:
        for number in range(1, 10):
            tile = str(number) + suit
            if app.hand.count(tile) >= 4:
                kanTiles.append(tile)
    return kanTiles


def get_player_chi_options(tile, discarderIndex):
    chiOptions = []
    
    if discarderIndex != 3:
        return chiOptions
        
    if tile in HonorOrder:
        return chiOptions
        
    number = int(tile[0])
    suit = tile[1]
        
    possibleSequences = [
        [number - 2, number - 1, number],
        [number - 1, number, number + 1],
        [number, number + 1, number + 2]
    ]
                
    for seq in possibleSequences:
        if min(seq) < 1 or max(seq) > 9:
            continue
            
        neededTiles = []
        for n in seq:
            seqTile = str(n) + suit
            if seqTile != tile:
                neededTiles.append(seqTile)
                
        if all(app.hand.count(neededTile) >= 1 for neededTile in neededTiles):
            chiOptions.append(neededTiles)
                    
    return chiOptions
    
def get_player_open_call_actions(tile, discarderIndex):
    actions = []

    if app.players[0]['riichiDeclared']:
        return actions
    
    if can_player_pon(tile):
        actions.append('Pon')
    
    if can_player_kan_on_discard(tile):
        actions.append('Kan')
        
    chiOptions = get_player_chi_options(tile, discarderIndex)
    if len(chiOptions) > 0:
        actions.append('Chi')
        
    return actions
    
def remove_last_discard_from_player(playerIndex):
    if len(app.players[playerIndex]['discards']) > 0:
        app.players[playerIndex]['discards'].pop()
        
def remove_tiles_from_hand(hand, tile, count):
    removed = 0
    i = 0
    
    while i < len(hand) and removed < count:
        if hand[i] == tile:
            hand.pop(i)
            removed += 1
        else:
            i += 1
            
def resolve_player_pon():
    tile = app.lastDiscardedTile
    discarder = app.lastDiscarder
    
    if tile == None or discarder == None:
        return
    
    remove_tiles_from_hand(app.hand, tile, 2)
    app.players[0]['calls'].append({
        'type': 'Pon',
        'tiles': [tile, tile, tile],
        'from': discarder
        })
        
    remove_last_discard_from_player(discarder)
    
    app.currentPlayer = 0
    app.aiThinking = False
    app.pendingAiPlayers = []
    app.drawnTile = None
    app.players[app.mainPlayerIndex]['lastDrawnTile'] = None
    app.selectedHandIndex = None
    app.previewTile = tile
    sort_hand(app.hand)
    update_no_yaku_warning()

def resolve_player_chi(chiTiles):
    tile = app.pendingCallTile
    discarder = app.pendingCallDiscarder
    
    if tile == None or discarder == None:
        return
    
    for chiTile in chiTiles:
        app.hand.remove(chiTile)
        
    fullCallTiles = chiTiles[:] + [tile]
    sort_hand(fullCallTiles)
    
    app.players[0]['calls'].append({
        'type': 'Chi',
        'tiles': fullCallTiles,
        'from': discarder
        })
        
    remove_last_discard_from_player(discarder)
    
    app.currentPlayer = 0
    app.aiThinking = False
    app.pendingAiPlayers = []
    app.drawnTile = None
    app.players[app.mainPlayerIndex]['lastDrawnTile'] = None
    app.selectedHandIndex = None
    app.previewTile = tile
    sort_hand(app.hand)
    
    app.pendingChiOptions = []
    app.pendingCallTile = None
    app.pendingCallDiscarder = None
    update_no_yaku_warning()


def resolve_player_closed_kan(tile):
    if app.hand.count(tile) < 4:
        return
    
    remove_tiles_from_hand(app.hand, tile, 4)
    app.players[0]['calls'].append({
        'type': 'Kan',
        'tiles': [tile, tile, tile, tile],
        'from': -1
        })
    
    app.currentPlayer = 0
    app.selectedHandIndex = None
    app.previewTile = tile
    sort_hand(app.hand)
    reveal_next_dora_indicator()
    
    # Draw a replacement tile
    draw_tile_for_player()
    
    update_no_yaku_warning()
    update_player_action_prompt()


def resolve_player_open_kan():
    tile = app.pendingKanTile
    discarder = app.pendingCallDiscarder
    
    if tile == None or discarder == None:
        return
    
    remove_tiles_from_hand(app.hand, tile, 3)
    app.players[0]['calls'].append({
        'type': 'Kan',
        'tiles': [tile, tile, tile, tile],
        'from': discarder
        })
    
    remove_last_discard_from_player(discarder)
    
    app.currentPlayer = 0
    app.aiThinking = False
    app.pendingAiPlayers = []
    app.selectedHandIndex = None
    app.previewTile = tile
    sort_hand(app.hand)
    reveal_next_dora_indicator()
    
    app.pendingKanTile = None
    app.pendingKanType = None
    
    # Draw a replacement tile
    draw_tile_for_player()
    
    update_no_yaku_warning()
    update_player_action_prompt()

def end_round_as_win(reason, winnerIndex=0, winningTile=None):
    scoreDetails = get_hand_yaku_and_score(reason.lower(), winnerIndex, winningTile, includeDora=True)
    app.handOver = True
    app.roundWinnerIndex = winnerIndex
    app.roundResult = 'win' if winnerIndex == app.mainPlayerIndex else 'loss'
    winnerName = get_player_display_name(winnerIndex)
    if winnerIndex == app.mainPlayerIndex:
        app.roundResultReason = reason
    else:
        app.roundResultReason = winnerName + ' won by ' + reason
    app.roundScoreText = format_score_text(scoreDetails)
    app.roundYakuLines = format_yaku_lines(scoreDetails)
    app.actionPromptOpen = False
    app.actionOptions = []
    app.aiThinking = False
    
def end_round_as_loss(reason):
    app.handOver = True
    app.roundResult = 'loss'
    app.roundResultReason = reason
    app.actionPromptOpen = False
    app.actionOptions = []
    app.aiThinking = False

def handle_action_button(action):
    
    # wasReactionPrompt is true for reactions to OTHER PLAYERS' discards (Ron, Pon, Chi, open Kan)
    # NOT for closed kans, which are player actions on their own turn
    wasReactionPrompt = (
        'Ron' in app.actionOptions or
        'Pon' in app.actionOptions or
        'Chi' in app.actionOptions or
        'Kan' in app.actionOptions  # only open kan on discard, not closed kans
        )
    
    if action == 'Tsumo':
        app.gameMessage = 'TSUMO!'
        end_round_as_win('Tsumo')
        
    elif action == 'Ron':
        app.gameMessage = 'RON!'
        end_round_as_win('Ron')
        
    elif action == 'Pon':
        resolve_player_pon()
        app.gameMessage = 'PON'
        app.actionPromptOpen = False
        app.actionOptions = []
        
    elif action == 'Chi':
        app.pendingChiOptions = get_player_chi_options(app.lastDiscardedTile, app.lastDiscarder)
        app.pendingCallTile = app.lastDiscardedTile
        app.pendingCallDiscarder = app.lastDiscarder
        show_player_chi_choice_prompt()
    
    elif action.startswith('Chi '):
        chosenChiTiles = None
        
        for chiTiles in app.pendingChiOptions:
            if chi_option_to_text(chiTiles, app.pendingCallTile) == action:
                chosenChiTiles = chiTiles
                break
            
        if chosenChiTiles != None:
            resolve_player_chi(chosenChiTiles)
            app.gameMessage = 'CHI'
            app.actionPromptOpen = False
            app.actionOptions = []
    
    elif action.startswith('Kan '):
        kanTile = action[4:]
        resolve_player_closed_kan(kanTile)
        app.gameMessage = 'KAN'
    
    elif action == 'Kan':
        resolve_player_open_kan()
        app.gameMessage = 'KAN'

    elif action == 'Riichi':
        app.players[0]['riichiDeclared'] = True
        app.gameMessage = 'RIICHI'
        app.actionPromptOpen = False
        app.actionOptions = []
        app.selectedHandIndex = None
        
    elif action == 'Pass':
        app.actionPromptOpen = False
        app.actionOptions = []
        app.pendingChiOptions = []
        app.pendingCallTile = None
        app.pendingCallDiscarder = None
        app.pendingKanTile = None
        app.pendingKanType = None
        
        if wasReactionPrompt:
            if len(app.pendingAiPlayers) > 0:
                app.aiThinking = True
                app.aiDelayCounter = app.aiTurnDelay
                app.currentPlayer = app.pendingAiPlayers[0]
            else:
                app.currentPlayer = 0
                draw_tile_for_player()
                update_player_action_prompt()

def check_wall_empty_loss():
    if len(app.wall) == 0 and app.handOver == False:
        end_round_as_loss('Wall Exhausted')
        return True
    return False

def update_room():
    if app.moveUp:
        app.playerY -= app.playerSpeed
    if app.moveDown:
        app.playerY += app.playerSpeed
    if app.moveLeft:
        app.playerX -= app.playerSpeed
    if app.moveRight:
        app.playerX += app.playerSpeed

    if app.playerX < app.playerSize / 2:
        app.playerX = app.playerSize / 2
    if app.playerX > 400 - app.playerSize / 2:
        app.playerX = 400 - app.playerSize / 2
    if app.playerY < app.playerSize / 2:
        app.playerY = app.playerSize / 2
    if app.playerY > 400 - app.playerSize / 2:
        app.playerY = 400 - app.playerSize / 2

    update_room_interaction_state()

def onStep():
    if app.currentScene == 'room':
        update_room()
        redraw_game()
        return

    if app.handOver == True:
        return
    
    if app.aiThinking == False:
        return
    
    if check_wall_empty_loss():
        redraw_game()
        return
    
    if len(app.pendingAiPlayers) == 0:
        app.aiThinking = False
        app.currentPlayer = 0
        
        if len(app.wall) == 0:
            end_round_as_loss('Wall Exhausted')
            redraw_game()
            return
        
        draw_tile_for_player()
        update_player_action_prompt()
        redraw_game()
        return
        
    app.aiDelayCounter -= 1
    if app.aiDelayCounter > 0:
        return
    
    currentAi = app.pendingAiPlayers.pop(0)
    app.currentPlayer = currentAi
    
    draw_tile_for_ai(currentAi)
    ai_discard_random_tile(currentAi)
    update_player_ron_prompt()
    
    if app.actionPromptOpen == False:
        openCallActions = get_player_open_call_actions(app.lastDiscardedTile, currentAi)
        if len(openCallActions) > 0:
            app.pendingCallTile = app.lastDiscardedTile
            app.pendingKanTile = app.lastDiscardedTile
            app.pendingCallDiscarder = currentAi
            show_player_discard_call_options(openCallActions)
            
    redraw_game()
    
    if app.actionPromptOpen:
        app.aiThinking = False
        return
    
    if len(app.pendingAiPlayers) > 0:
        app.currentPlayer = app.pendingAiPlayers[0]
        app.aiDelayCounter = app.aiTurnDelay
    else:
        app.aiDelayCounter = app.aiTurnDelay
                
def onKeyPress(key):
    if app.currentScene == 'room':
        if key == 'w':
            app.moveUp = True
        elif key == 's':
            app.moveDown = True
        elif key == 'a':
            app.moveLeft = True
        elif key == 'd':
            app.moveRight = True
        elif key == 'e':
            if app.playerNearTutorialNpc:
                app.currentScene = 'mahjong'
                app.tutorialOpen = True
                app.tutorialPage = 0
                redraw_game()
            elif app.playerNearTable:
                app.currentScene = 'mahjong'
                redraw_game()
            elif app.playerNearHandSelectTable:
                app.currentScene = 'handSelect'
                app.customHandInput = ''
                app.customHandError = ''
                redraw_game()
        return
    
    if app.currentScene == 'handSelect':
        if key == 'escape':
            app.currentScene = 'room'
            app.customHandInput = ''
            app.customHandError = ''
            redraw_game()
            return
        elif key == 'backspace':
            app.customHandInput = app.customHandInput[:-1]
            app.customHandError = ''
            redraw_game()
            return
        elif key == 'enter':
            # Treat enter as submit
            hand, error = validate_and_parse_hand(app.customHandInput)
            if error:
                app.customHandError = error
                redraw_game()
            else:
                start_with_custom_hand(hand)
                app.customHandInput = ''
                app.customHandError = ''
            return
        else:
            # Add character to input
            if len(key) == 1:
                app.customHandInput += key
                app.customHandError = ''
                redraw_game()
        return

    if app.currentScene == 'mahjong':
        if key == 'escape':
            app.currentScene = 'room'
            redraw_game()
            return

def onKeyRelease(key):
    if key == 'w':
        app.moveUp = False
    elif key == 's':
        app.moveDown = False
    elif key == 'a':
        app.moveLeft = False
    elif key == 'd':
        app.moveRight = False

def onMousePress(mouseX, mouseY):
    if app.currentScene == 'handSelect':
        for target in app.handSelectionButtonTargets:
            if point_in_rect(mouseX, mouseY, target['x'], target['y'], target['w'], target['h']):
                if target['type'] == 'inputBox':
                    # Focus on input box (just for visual feedback)
                    pass
                elif target['type'] == 'submit':
                    # Parse and validate the input
                    hand, error = validate_and_parse_hand(app.customHandInput)
                    if error:
                        app.customHandError = error
                        redraw_game()
                    else:
                        # Valid hand, start the game
                        start_with_custom_hand(hand)
                        app.customHandInput = ''
                        app.customHandError = ''
                    return
                elif target['type'] == 'clear':
                    app.customHandInput = ''
                    app.customHandError = ''
                    redraw_game()
                    return
        return
    
    if app.currentScene != 'mahjong':
        return
    if app.tutorialOpen:
        for target in app.tutorialButtonTargets:
            if point_in_rect(mouseX, mouseY, target['x'], target['y'], target['w'], target['h']):
                if target['type'] == 'tutorialBack':
                    app.tutorialOpen = False
                    app.tutorialPage = 0
                    app.currentScene = 'room'
                elif target['type'] == 'tutorialPrev':
                    app.tutorialPage -= 1
                elif target['type'] == 'tutorialNext':
                    app.tutorialPage += 1
                redraw_game()
                return
        return
                    
    if app.handOver:
        if app.resultButtonTarget != None:
            if point_in_rect(mouseX, mouseY,
            app.resultButtonTarget['x'],
            app.resultButtonTarget['y'],
            app.resultButtonTarget['w'],
            app.resultButtonTarget['h']):
                start_new_hand()
        return

    
    if app.aiThinking:
        return
    
    if app.actionPromptOpen:
        for target in app.actionButtonTargets:
            if point_in_rect(mouseX, mouseY, target['x'], target['y'], target['w'], target['h']):
                handle_action_button(target['action'])
                redraw_game()
                return
        return
    
    for target in app.clickTargets:
        if point_in_rect(mouseX, mouseY, target['x'], target['y'], target['w'], target['h']):
            if target['type'] == 'hand' or target['type'] == 'drawnTile':
                clickedIndex = target['index']
                                
                if app.selectedHandIndex == clickedIndex:
                    discard_selected_tile()
                else:
                    app.selectedHandIndex = clickedIndex
                    app.previewTile = target['tile']
                    redraw_game()
                return
                    
            elif target['type'] == 'discardPreview':
                app.previewTile = target['tile']
                redraw_game()
                return
    
redraw_game()
    
cmu_graphics.run()







