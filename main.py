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
app.roundResult = None
app.roundResultReason = ''
app.noYakuWarning = ''
app.resultButtonTarget = None
app.tutorialOpen = False
app.tutorialPage = 0
app.tutorialButtonTargets = []

TileIndexMap = {
    '1m': 0, '2m': 1, '3m': 2, '4m': 3, '5m': 4, '6m': 5, '7m': 6, '8m': 7, '9m': 8,
    '1p': 9, '2p': 10, '3p': 11, '4p': 12, '5p': 13, '6p': 14, '7p': 15, '8p': 16, '9p': 17,
    '1s': 18, '2s': 19, '3s': 20, '4s': 21, '5s': 22, '6s': 23, '7s': 24, '8s': 25, '9s': 26,
    'E': 27, 'S': 28, 'W': 29, 'N': 30, 'Wh': 31, 'G': 32, 'R': 33
    }

TileWidth = 24
TileHeight = 36
TileGap = 2

HandY = 400 - 52

SuitOrder = {'m': 0, 'p': 1, 's': 2}
HonorOrder = {'E': 0, 'S': 1, 'W': 2, 'N': 3, 'Wh': 4, 'G': 5, 'R': 6}

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
    app.roundResult = None
    app.roundResultReason = ''
    app.noYakuWarning = ''
    app.resultButtonTarget = None
    app.tutorialOpen = False
    app.tutorialPage = 0
    app.tutorialButtonTargets = []
    
def deal_starting_hands():
    newWall = build_wall()
    random.shuffle(newWall)
        

    players = [
        {'hand': [], 'discards': [], 'calls': [], 'isMenzenchin': True},
        {'hand': [], 'discards': [], 'calls': [], 'isMenzenchin': True},
        {'hand': [], 'discards': [], 'calls': [], 'isMenzenchin': True},
        {'hand': [], 'discards': [], 'calls': [], 'isMenzenchin': True}
    ]

    for roundNumber in range(13):
        for playerIndex in range(4):
            players[playerIndex]['hand'].append(newWall.pop())
        
    players[0]['hand'].append(newWall.pop())
    
    for player in players:
        sort_hand(player['hand'])
        
    return players, newWall

app.players, app.wall = deal_starting_hands()
app.hand = app.players[0]['hand']

# total width of 14 tiles with gaps
app.TotalHandWidth = len(app.hand) * TileWidth + (len(app.hand) - 1) * TileGap 
app.HandX = (400 - app.TotalHandWidth) / 2

app.selectedHandIndex = None
app.previewTile = None
app.clickTargets = []
app.scene = Group()
app.noYakuWarning = ''


def draw_tile_base(x, y):
        app.scene.add(Rect(x, y, TileWidth, TileHeight, fill='ivory', border='black', borderWidth=1))
        app.scene.add(Rect(x + 1, y + 1, TileWidth - 2, TileHeight - 2, fill=rgb(248, 244, 232), opacity=40))
            
            
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
            
            
def draw_tile(x, y, tile):
    draw_tile_base(x, y)
        
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
                    
                    
def draw_selected_outline(x, y):
    app.scene.add(Rect(x - 1, y - 1, TileWidth + 2, TileHeight + 2, fill=None, border='red', borderWidth=2))
    
def draw_preview_panel():
    app.scene.add(Rect(330, 5, 65, 95, fill='white', border='black', borderWidth=2))

    if app.previewTile != None:
        previewX = 331
        previewY = 6
        
        # big boy tile
        app.scene.add(Rect(previewX, previewY, 63, 93, fill='ivory', border='black', borderWidth=1))
        app.scene.add(Rect(previewX + 1, previewY + 1, 61, 91, fill=rgb(248, 244, 232), opacity=40))
        
        tile = app.previewTile
        

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
                        
def draw_mini_tile(x, y, tile, rotateAngle=0):
    app.scene.add(Rect(x, y, 20, 30, fill='ivory', border='black', borderWidth=1, rotateAngle=rotateAngle))
          
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
        draw_mini_tile(x, y, tile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': tile, 'x': x, 'y': y, 'w': 20, 'h': 30})
        
    elif len(rightDiscards) == 2:
        newestTile = rightDiscards[-1]
        olderTile = rightDiscards[-2]
        
        draw_mini_tile(255, 216, newestTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 255, 'y': 216, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 192, olderTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': olderTile, 'x': 255, 'y': 192, 'w': 20, 'h': 30})
        
    else:
        visibleRightDiscards = rightDiscards[-3:]
        
        newestTile = visibleRightDiscards[-1]
        middleTile = visibleRightDiscards[-2]
        oldestTile = visibleRightDiscards[-3]
        
        draw_mini_tile(255, 216, newestTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': newestTile, 'x': 255, 'y': 216, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 192, middleTile, rotateAngle=90)
        app.clickTargets.append({'type': 'discardPreview', 'tile': middleTile, 'x': 255, 'y': 192, 'w': 20, 'h': 30})
        
        draw_mini_tile(255, 168, oldestTile, rotateAngle=90)
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
    
def get_player_call_meld_count():
    return len(app.players[0]['calls'])

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

def is_standard_win_with_calls(concealedTiles):
    totalMeldsNeededFromHand = 4 - get_player_call_meld_count()
    
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
    
    
def get_all_tiles_for_yaku_check(winType):
    fullHand = app.hand[:]
    
    if winType == 'tsumo':
        if app.drawnTile != None:
            fullHand.append(app.drawnTile)
    elif winType == 'ron':
        if app.lastDiscardedTile != None:
            fullHand.append(app.lastDiscardedTile)
            
    for call in app.players[0]['calls']:
        for tile in call['tiles']:
            fullHand.append(tile)
            
    return fullHand
            
            
def has_player_yaku(winType):
    fullTiles = get_all_tiles_for_yaku_check(winType)
    
    if app.players[0]['isMenzenchin'] and winType == 'tsumo':
        return True
        
    if hand_has_triplet(fullTiles, 'E'):
        return True
        
    if hand_has_triplet(fullTiles, 'Wh'):
        return True
    
    if hand_has_triplet(fullTiles, 'G'):
        return True
        
    if hand_has_triplet(fullTiles, 'R'):
        return True
        
    return False

def update_player_action_prompt():
    app.actionOptions = []
    app.actionPromptOpen = False
    
    if app.currentPlayer != 0:
        return
    
    fullHand = app.hand[:]
    if app.drawnTile != None:
        fullHand.append(app.drawnTile)
        
    if is_standard_win_with_calls(fullHand) and has_player_yaku('tsumo'):
        app.actionOptions = ['Tsumo', 'Pass']
        app.actionPromptOpen = True

def update_player_ron_prompt():
    app.actionOptions = []
    app.actionPromptOpen = False
    
    if app.lastDiscardedTile == None:
        return
    
    fullHand = app.hand[:]
    fullHand.append(app.lastDiscardedTile)
    
    if is_standard_win_with_calls(fullHand) and has_player_yaku('ron'):
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
    if app.players[playerIndex]['isMenzenchin']:
        return 'Menzenchin'
    return 'Open Hand'

def start_new_hand():
    reset_round_state()
    app.players, app.wall = deal_starting_hands()
    app.hand = app.players[0]['hand']
    
    app.TotalHandWidth = len(app.hand) * TileWidth + (len(app.hand) - 1) * TileGap
    app.HandX = (400 - app.TotalHandWidth) / 2
    
    redraw_game()

def draw_round_result_overlay():
    app.resultButtonTarget = None
    
    if app.roundResult == None:
        return
    
    app.scene.add(Rect(0, 0, 400, 400, fill='black', opacity=55))
    
    if app.roundResult == 'win':
        app.scene.add(Label('YOU WIN', 200, 170, size=28, fill='gold', bold=True))
        app.scene.add(Label(app.roundResultReason, 200, 205, size=18, fill='white', bold=True))
    elif app.roundResult == 'loss':
        app.scene.add(Label('YOU LOSE', 200, 170, size=28, fill='red', bold=True))
        app.scene.add(Label(app.roundResultReason, 200, 205, size=18, fill='white', bold=True))
        
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


#Not a proper Furiten warning, just calls out no current Yaku if open hand FIX THIS LATER
def update_no_yaku_warning():
    app.noYakuWarning = ''
    
    if app.players[0]['isMenzenchin']:
        return
    
    possibleOpenYaku = False
    fullTiles = app.hand[:]
    
    for call in app.players[0]['calls']:
        for tile in call['tiles']:
            fullTiles.append(tile)
            
    if hand_has_triplet(fullTiles, 'E'):
        possibleOpenYaku = True
    if hand_has_triplet(fullTiles, 'Wh'):
        possibleOpenYaku = True
    if hand_has_triplet(fullTiles, 'G'):
        possibleOpenYaku = True
    if hand_has_triplet(fullTiles, 'R'):
        possibleOpenYaku = True
        
    if possibleOpenYaku == False:
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
    app.scene.add(Label('Menzen Tsumo / Closed Hand Draw', 200, 208, size=13, fill='white'))
    app.scene.add(Label('East triplet', 200, 228, size=13, fill='white'))
    app.scene.add(Label('White / Green / Red triplet', 200, 248, size=13, fill='white'))
    
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
        

def redraw_game():
    app.scene.clear()
    app.clickTargets = []
    
    app.scene.add(Rect(0, 0, 400, 400, fill=rgb(34, 120, 70)))
    
    app.scene.add(Rect(110, 110, 180, 180, fill=rgb(45, 140, 85), border=rgb(20, 90, 50)))
    #app.scene.add(Label('Center Table Space', 200, 200, size=16, fill='white', bold=True))
    
    app.scene.add(Rect(10, 10, 70, 35, fill='lightBlue', border='blue', borderWidth=2))
    app.scene.add(Label('Tutorial', 45, 27, size=12, fill='darkBlue', bold=True))
    
    app.clickTargets.append({
        'type': 'tutorialOpen',
        'x': 10,
        'y': 10,
        'w': 70,
        'h': 35
        })
    
    # discard history button ADD IN FUTURE
    #app.scene.add(Rect(10, 10, 60, 35, fill='lightBlue', border='blue', borderWidth=2))
    #app.scene.add(Label('Discards', 40, 27, size=12, fill='darkBlue', bold=True))
    
    app.scene.add(Label('Riichi Mahjong', 200, 25, size=18, fill='white', bold=True))
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
    
    for i in range(len(app.hand)):
        TileX = app.HandX + i * (TileWidth + TileGap)
        draw_tile(TileX, HandY, app.hand[i])

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
        draw_tile(drawnTileX, HandY, app.drawnTile)
        
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
    
    
def point_in_rect(mouseX, mouseY, rectX, rectY, rectW, rectH):
    return (
        mouseX >= rectX and
        mouseX <= rectX + rectW and
        mouseY >= rectY and
        mouseY <= rectY + rectH
        )
        
def draw_tile_for_player():
    if len(app.wall) == 0:
        return
    
    app.drawnTile = app.wall.pop()
    
def draw_tile_for_ai(playerIndex):
    if len(app.wall) == 0:
        return
    
    drawnTile = app.wall.pop()
    app.players[playerIndex]['hand'].append(drawnTile)
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
    sort_hand(app.players[playerIndex]['hand'])
    
def start_ai_turns():
    app.pendingAiPlayers = [3, 2, 1]
    app.aiThinking = True
    app.aiDelayCounter = app.aiTurnDelay
    app.currentPlayer = 3
    
def discard_selected_tile():
    if app.selectedHandIndex == None:
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
    
def set_player_open_hand(playerIndex):
    app.players[playerIndex]['isMenzenchin'] = False
    
def set_player_closed_hand(playerIndex):
    app.players[playerIndex]['isMenzenchin'] = True
    
def can_player_pon(tile):
    return app.hand.count(tile) >= 2
    
    
def can_player_kan_on_discard(tile):
    return app.hand.count(tile) >= 3
    
    
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
    
    if can_player_pon(tile):
        actions.append('Pon')
        
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
    set_player_open_hand(0)
    
    app.currentPlayer = 0
    app.aiThinking = False
    app.pendingAiPlayers = []
    app.drawnTile = None
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
    set_player_open_hand(0)
    
    app.currentPlayer = 0
    app.aiThinking = False
    app.pendingAiPlayers = []
    app.drawnTile = None
    app.selectedHandIndex = None
    app.previewTile = tile
    sort_hand(app.hand)
    
    app.pendingChiOptions = []
    app.pendingCallTile = None
    app.pendingCallDiscarder = None
    update_no_yaku_warning()

def end_round_as_win(reason):
    app.handOver = True
    app.roundResult = 'win'
    app.roundResultReason = reason
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
    
    wasReactionPrompt = (
        'Ron' in app.actionOptions or
        'Pon' in app.actionOptions or
        'Chi' in app.actionOptions or
        'Kan' in app.actionOptions
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
        
    elif action == 'Kan':
        set_player_open_hand(0)
        app.gameMessage = 'KAN'
        app.actionPromptOpen = False
        app.actionOptions = []
        
    elif action == 'Pass':
        app.actionPromptOpen = False
        app.actionOptions = []
        app.pendingChiOptions = []
        app.pendingCallTile = None
        app.pendingCallDiscarder = None
        
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

def onStep():
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
                
def toggle_player_menzenchin_for_test():
    app.players[0]['isMenzenchin'] = not app.players[0]['isMenzenchin']
    redraw_game()

def onKeyPress(key):
    if key == 'm':
        toggle_player_menzenchin_for_test()

def onMousePress(mouseX, mouseY):
    if app.tutorialOpen:
        for target in app.tutorialButtonTargets:
            if point_in_rect(mouseX, mouseY, target['x'], target['y'], target['w'], target['h']):
                if target['type'] == 'tutorialBack':
                    app.tutorialOpen = False
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
            if target['type'] == 'tutorialOpen':
                app.tutorialOpen = True
                app.tutorialPage = 0
                redraw_game()
                return
            
            elif target['type'] == 'hand' or target['type'] == 'drawnTile':
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
    

    
    
    
    

