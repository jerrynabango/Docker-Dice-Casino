from flask import Flask, render_template_string, request, jsonify, session
import redis
import random
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dice-casino-secret-key')

# Connect to Redis
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# HTML Template with Game Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎲 Docker Dice Casino</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 3em;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        }
        .game-info {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .game-info p {
            margin: 5px 0;
        }
        .main-game {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .game-area {
            background: rgba(255,255,255,0.15);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .dice {
            font-size: 120px;
            margin: 20px 0;
            animation: shake 0.5s ease-in-out;
        }
        @keyframes shake {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(10deg); }
            75% { transform: rotate(-10deg); }
        }
        .bet-area {
            margin: 20px 0;
        }
        input, select, button {
            padding: 12px 20px;
            font-size: 16px;
            margin: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }
        input {
            width: 150px;
            text-align: center;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
        button:active {
            transform: scale(0.95);
        }
        .result {
            font-size: 20px;
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.5s;
        }
        .win {
            background: rgba(0,255,0,0.3);
            border: 2px solid #00ff00;
        }
        .lose {
            background: rgba(255,0,0,0.3);
            border: 2px solid #ff0000;
        }
        .leaderboard {
            background: rgba(255,255,255,0.15);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .leaderboard h3 {
            text-align: center;
            margin-bottom: 15px;
        }
        .leaderboard table {
            width: 100%;
            border-collapse: collapse;
        }
        .leaderboard td, .leaderboard th {
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .player-stats {
            display: inline-block;
            background: rgba(0,0,0,0.3);
            padding: 10px 20px;
            border-radius: 10px;
            margin: 10px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .container-id {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎲 Docker Dice Casino 🐳</h1>
            <p>Container: {{ container_id[:12] }} | Player: {{ player_name }}</p>
        </div>

        <div class="game-info">
            <div class="player-stats">
                💰 Balance: <strong>${{ balance }}</strong>
            </div>
            <div class="player-stats">
                🎮 Games Played: <strong>{{ games_played }}</strong>
            </div>
            <div class="player-stats">
                🏆 Win Rate: <strong>{{ win_rate }}%</strong>
            </div>
        </div>

        <div class="main-game">
            <div class="game-area">
                <h2>🎲 Roll the Dice!</h2>
                <div class="dice" id="dice">🎲</div>
                
                <form id="betForm">
                    <div class="bet-area">
                        <select name="bet_type" id="bet_type">
                            <option value="over">Over 3.5 (2x payout)</option>
                            <option value="under">Under 3.5 (2x payout)</option>
                            <option value="exact">Exact Number (5x payout)</option>
                        </select>
                        <input type="number" name="bet_amount" id="bet_amount" placeholder="Bet amount" min="1" required>
                        <input type="number" name="exact_number" id="exact_number" placeholder="Exact number (1-6)" min="1" max="6" disabled>
                        <button type="submit">🎲 PLACE BET!</button>
                    </div>
                </form>
                
                <div id="result" class="result"></div>
            </div>

            <div class="leaderboard">
                <h3>🏆 Global Leaderboard 🏆</h3>
                <table id="leaderboard">
                    <thead>
                        <tr><th>Rank</th><th>Player</th><th>Balance</th><th>Games</th><th>Win Rate</th></tr>
                    </thead>
                    <tbody id="leaderboardBody">
                        {% for player in leaderboard %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ player.name }}</td>
                            <td>${{ player.balance }}</td>
                            <td>{{ player.games }}</td>
                            <td>{{ player.win_rate }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="container-id">
            🐳 Running in Docker Container | Data stored in Redis
        </div>
    </div>

    <script>
        // Handle bet form submission
        document.getElementById('betForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const betType = document.getElementById('bet_type').value;
            const betAmount = document.getElementById('bet_amount').value;
            const exactNumber = document.getElementById('exact_number').value;
            
            // Disable form during roll
            const submitBtn = e.target.querySelector('button');
            submitBtn.disabled = true;
            submitBtn.textContent = '🎲 Rolling...';
            
            // Animate dice
            const dice = document.getElementById('dice');
            let rolls = 0;
            const interval = setInterval(() => {
                const randomDice = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][Math.floor(Math.random() * 6)];
                dice.textContent = randomDice;
                rolls++;
                if (rolls > 10) clearInterval(interval);
            }, 100);
            
            // Send bet to server
            const response = await fetch('/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    bet_type: betType,
                    bet_amount: parseInt(betAmount),
                    exact_number: exactNumber ? parseInt(exactNumber) : null
                })
            });
            
            const data = await response.json();
            
            // Show final dice
            clearInterval(interval);
            const finalDice = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][data.dice_roll - 1];
            dice.textContent = finalDice;
            
            // Show result
            const resultDiv = document.getElementById('result');
            if (data.win) {
                resultDiv.className = 'result win';
                resultDiv.innerHTML = `🎉 WIN! 🎉<br>You won $${data.win_amount}!<br>${data.message}`;
            } else {
                resultDiv.className = 'result lose';
                resultDiv.innerHTML = `😢 LOSS! 😢<br>You lost $${data.bet_amount}!<br>${data.message}`;
            }
            
            // Refresh page data after 1 second
            setTimeout(() => {
                location.reload();
            }, 2000);
        });
        
        // Enable/disable exact number input based on bet type
        document.getElementById('bet_type').addEventListener('change', (e) => {
            const exactInput = document.getElementById('exact_number');
            exactInput.disabled = e.target.value !== 'exact';
        });
    </script>
</body>
</html>
"""

def get_player_id():
    """Get or create player ID in session"""
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid4())
        # Initialize player in Redis
        player_key = f"player:{session['player_id']}"
        redis_client.hset(player_key, mapping={
            'name': f"Player_{random.randint(1000, 9999)}",
            'balance': '1000',
            'games_played': '0',
            'games_won': '0'
        })
    return session['player_id']

def get_player_stats(player_id):
    """Get player statistics from Redis"""
    player_key = f"player:{player_id}"
    data = redis_client.hgetall(player_key)
    if not data:
        return None
    
    games_played = int(data.get('games_played', 0))
    games_won = int(data.get('games_won', 0))
    win_rate = (games_won / games_played * 100) if games_played > 0 else 0
    
    return {
        'name': data.get('name', 'Unknown'),
        'balance': int(data.get('balance', 1000)),
        'games_played': games_played,
        'games_won': games_won,
        'win_rate': round(win_rate, 1)
    }

def update_player_stats(player_id, won, bet_amount, win_amount=0):
    """Update player statistics in Redis"""
    player_key = f"player:{player_id}"
    
    redis_client.hincrby(player_key, 'games_played', 1)
    if won:
        redis_client.hincrby(player_key, 'games_won', 1)
        redis_client.hincrby(player_key, 'balance', win_amount)
    else:
        redis_client.hincrby(player_key, 'balance', -bet_amount)

def get_leaderboard():
    """Get top 10 players from Redis"""
    players = []
    # Get all player keys
    for key in redis_client.scan_iter("player:*"):
        player_id = key.split(':')[1]
        stats = get_player_stats(player_id)
        if stats:
            players.append(stats)
    
    # Sort by balance
    players.sort(key=lambda x: x['balance'], reverse=True)
    return players[:10]

@app.route('/')
def index():
    """Main game page"""
    player_id = get_player_id()
    stats = get_player_stats(player_id)
    
    if not stats:
        return "Error loading player data", 500
    
    leaderboard = get_leaderboard()
    container_id = os.environ.get('HOSTNAME', 'unknown')
    
    return render_template_string(
        HTML_TEMPLATE,
        player_name=stats['name'],
        balance=stats['balance'],
        games_played=stats['games_played'],
        win_rate=stats['win_rate'],
        leaderboard=leaderboard,
        container_id=container_id
    )

@app.route('/play', methods=['POST'])
def play():
    """Handle bet placement and dice roll"""
    player_id = get_player_id()
    stats = get_player_stats(player_id)
    
    if not stats:
        return jsonify({'error': 'Player not found'}), 404
    
    data = request.json
    bet_type = data.get('bet_type')
    bet_amount = data.get('bet_amount', 0)
    exact_number = data.get('exact_number')
    
    # Validate bet
    if bet_amount <= 0 or bet_amount > stats['balance']:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    # Roll dice
    dice_roll = random.randint(1, 6)
    
    # Calculate win/loss
    win = False
    win_amount = 0
    message = ""
    
    if bet_type == 'over':
        if dice_roll > 3:
            win = True
            win_amount = bet_amount * 2
            message = f"Dice rolled {dice_roll}! (Over 3.5)"
        else:
            message = f"Dice rolled {dice_roll}! (Under 3.5)"
    
    elif bet_type == 'under':
        if dice_roll < 4:
            win = True
            win_amount = bet_amount * 2
            message = f"Dice rolled {dice_roll}! (Under 3.5)"
        else:
            message = f"Dice rolled {dice_roll}! (Over 3.5)"
    
    elif bet_type == 'exact':
        if exact_number and dice_roll == exact_number:
            win = True
            win_amount = bet_amount * 5
            message = f"Dice rolled {dice_roll}! Exactly right!"
        else:
            message = f"Dice rolled {dice_roll}! Not a match."
    
    # Update player stats
    update_player_stats(player_id, win, bet_amount, win_amount if win else 0)
    
    return jsonify({
        'win': win,
        'dice_roll': dice_roll,
        'win_amount': win_amount if win else 0,
        'bet_amount': bet_amount,
        'message': message,
        'new_balance': stats['balance'] + (win_amount if win else -bet_amount)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)