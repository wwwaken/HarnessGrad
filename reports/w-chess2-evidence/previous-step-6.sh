python3 -c "
import socket
import json
import sys

sock_path = '/tmp/hg-stepwise-74i44xz0/stepwise.sock'

try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sock_path)
    
    # Read observation
    data = sock.recv(4096)
    if data:
        obs = json.loads(data.decode('utf-8'))
        print('Observation:', json.dumps(obs, indent=2))
        
        # Check status
        status = obs.get('status')
        if status == 'solved':
            print('Already solved')
            sys.exit(0)
        if status == 'failed':
            print('Already failed')
            sys.exit(0)
        
        # Get FEN and turn
        fen = obs.get('fen')
        solver_turn = obs.get('solver_turn', True)
        
        print('FEN:', fen)
        print('Solver turn:', solver_turn)
        
        # Parse FEN to get board state
        # For now, let's just print and wait for more info
        
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
"
