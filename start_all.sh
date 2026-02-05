# 1. ������������ ���� � �����
APP_DIR="/root/drun"
cd $APP_DIR

# 2. ������� ������
echo "--- ������� ������� ---"
fuser -k 3000/tcp > /dev/null 2>&1
pkill -f cloudflared
# ������� ������ �����, ����� �� �������������
pkill -f "main.py" 
sleep 2

# 3. ������ �������
echo "--- ������ ������� Cloudflare ---"
rm -f tunnel.log
stdbuf -oL cloudflared tunnel --url http://localhost:3000 > tunnel.log 2>&1 &

echo -n "�������� ������"
TUNNEL_URL=""
for i in {1..20}; do
    echo -n "."
    TUNNEL_URL=$(grep -o 'https://[-a-z0-9.]*\.trycloudflare.com' tunnel.log | head -n 1)
    if [ ! -z "$TUNNEL_URL" ]; then
        break
    fi
    sleep 1
done
echo ""

if [ -z "$TUNNEL_URL" ]; then
    echo "������: �� ������� �������� ������."
    exit 1
fi
echo "������: $TUNNEL_URL"

# 4. ���������� settings.json
if [ ! -f "settings.json" ]; then echo "{}" > settings.json; fi
tmp=$(mktemp)
jq ".api_url = \"$TUNNEL_URL\"" settings.json > "$tmp" && mv "$tmp" settings.json

# 5. �����: ����������� ���������
export PYTHONPATH=/usr/local/lib/python3.10/dist-packages:$PYTHONPATH

echo "--- ������ ���� ---"
python3.10 -W ignore main.py