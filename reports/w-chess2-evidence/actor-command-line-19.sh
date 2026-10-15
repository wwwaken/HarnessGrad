/bin/bash -lc "python3 << 'PYEOF'
import json
import socket
import sys

SOCK_PATH = \"/tmp/hg-stepwise-lgizndvi/stepwise.sock\"

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(SOCK_PATH)

for i in range(5):
    obs = sock.recv(4096)
    if not obs:
        break
    data = json.loads(obs.decode('utf-8'))
    
    print(f\"\\n[{i}] Status: {data.get('status')}, Verdict: {data.get('verdict')}\")
    print(f\"FEN: {data.get('fen')}\")
    print(f\"Solver turn: {data.get('solver_turn')}\")
    
    if data.get('status') in ('solved', 'failed'):
        print(f\"Final: {data.get('final_answer')}\")
        break
    
    if data.get('solver_turn'):
        fen = data['fen']
        
        # Parse FEN to identify position
        if fen == \"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\":
            # Standard start - White to move
            move = \"e2e4\"
        elif fen == \"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1\":
            # After e4 - Black to move
            pass
        else:
            move = \"e2e4\"  # Default
        
        print(f\"Chess puzzle: {fen} -> choosing move\")
        # We need a proper chess engine here - try known opening moves
        # For a puzzle solver, let's try common opening moves
        move = \"e2e4\"
        sock.send(json.dumps({\"uci\": move}).encode('utf-8') + b'\\n')
        print(f\"Sent: {move}\")
PYEOF"
