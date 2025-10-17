#!/bin/bash
# SDN Projesi Başlatma Scripti

echo "╔════════════════════════════════════════════════════════╗"
echo "║   SDN Tabanlı Dinamik Yönlendirme Sistemi             ║"
echo "║   Startup Script                                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Gerekli komutları kontrol et
echo "Checking requirements..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

all_ok=true

if ! check_command python3; then
    all_ok=false
fi

if ! check_command pip3; then
    all_ok=false
fi

if ! command -v mn &> /dev/null; then
    echo -e "${RED}✗${NC} Mininet is not installed"
    all_ok=false
else
    echo -e "${GREEN}✓${NC} Mininet is installed"
fi

if ! command -v ryu-manager &> /dev/null; then
    echo -e "${RED}✗${NC} Ryu Controller is not installed"
    all_ok=false
else
    echo -e "${GREEN}✓${NC} Ryu Controller is installed"
fi

if [ "$all_ok" = false ]; then
    echo ""
    echo -e "${RED}Missing requirements!${NC}"
    echo "Please run: pip3 install -r requirements.txt"
    echo "And follow docs/INSTALLATION.md for complete setup"
    exit 1
fi

echo ""
echo -e "${GREEN}All requirements satisfied!${NC}"
echo ""

# Temizlik
echo "Cleaning up previous Mininet instances..."
sudo mn -c > /dev/null 2>&1
pkill -f ryu-manager > /dev/null 2>&1

echo ""
echo "Select a controller to start:"
echo "1. Shortest Path Controller"
echo "2. Load Balancing Controller"
echo "3. QoS-Based Controller"
echo ""
read -p "Enter choice (1-3): " controller_choice

case $controller_choice in
    1)
        CONTROLLER="controllers/shortest_path_controller.py"
        echo -e "${GREEN}Starting Shortest Path Controller...${NC}"
        ;;
    2)
        CONTROLLER="controllers/load_balancing_controller.py"
        echo -e "${GREEN}Starting Load Balancing Controller...${NC}"
        ;;
    3)
        CONTROLLER="controllers/qos_controller.py"
        echo -e "${GREEN}Starting QoS-Based Controller...${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo ""
echo "Select a topology:"
echo "1. Simple Topology (4 switches, 4 hosts)"
echo "2. Complex Topology (8 switches, 8 hosts)"
echo ""
read -p "Enter choice (1-2): " topo_choice

case $topo_choice in
    1)
        TOPOLOGY="topologies/simple_topology.py"
        echo -e "${GREEN}Using Simple Topology${NC}"
        ;;
    2)
        TOPOLOGY="topologies/complex_topology.py"
        echo -e "${GREEN}Using Complex Topology${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════"
echo "Starting SDN Network..."
echo "════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}Controller:${NC} $CONTROLLER"
echo -e "${YELLOW}Topology:${NC} $TOPOLOGY"
echo ""

# Controller'ı arka planda başlat
echo "Starting controller in background..."
ryu-manager $CONTROLLER > logs/controller.log 2>&1 &
CONTROLLER_PID=$!
echo "Controller PID: $CONTROLLER_PID"

# Controller'ın başlamasını bekle
sleep 3

# Controller çalışıyor mu kontrol et
if ps -p $CONTROLLER_PID > /dev/null; then
    echo -e "${GREEN}✓ Controller is running${NC}"
else
    echo -e "${RED}✗ Controller failed to start${NC}"
    echo "Check logs/controller.log for details"
    exit 1
fi

echo ""
echo "Starting Mininet topology..."
echo ""

# Temizlik fonksiyonu
cleanup() {
    echo ""
    echo "Shutting down..."
    sudo mn -c > /dev/null 2>&1
    kill $CONTROLLER_PID > /dev/null 2>&1
    echo "Cleanup complete!"
    exit 0
}

# SIGINT yakalandığında temizlik yap
trap cleanup SIGINT SIGTERM

# Mininet'i başlat
sudo python3 $TOPOLOGY

# Mininet kapandıktan sonra temizlik
cleanup
