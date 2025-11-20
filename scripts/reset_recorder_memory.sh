#!/bin/bash
#
# Reset Olympus Transcriber Memory
# 
# Ten skrypt resetuje "pamięć" systemu transkrypcji, co powoduje że 
# przy następnym uruchomieniu zobaczy wszystkie pliki utworzone po 18 listopada 2025.
#
# Użycie:
#   bash scripts/reset_recorder_memory.sh
#   lub
#   bash scripts/reset_recorder_memory.sh 2025-11-18
#

set -e

# Kolory dla outputu
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

STATE_FILE="$HOME/.olympus_transcriber_state.json"
BACKUP_FILE="$HOME/.olympus_transcriber_state.json.backup"

# Data do ustawienia (domyślnie 18 listopada 2025 00:00:00)
# Można przekazać jako argument: ./reset_recorder_memory.sh 2025-11-15
TARGET_DATE="${1:-2025-11-18}"

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Reset Olympus Transcriber Memory${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Sprawdź czy plik state istnieje
if [ -f "$STATE_FILE" ]; then
    echo -e "${YELLOW}📁 Znaleziono istniejący plik state:${NC}"
    echo "   $STATE_FILE"
    echo ""
    
    # Pokaż obecny last_sync
    if command -v jq &> /dev/null; then
        CURRENT_SYNC=$(jq -r '.last_sync' "$STATE_FILE" 2>/dev/null || echo "N/A")
        echo -e "${YELLOW}📅 Obecny last_sync:${NC} $CURRENT_SYNC"
    else
        echo -e "${YELLOW}📅 Obecna zawartość:${NC}"
        cat "$STATE_FILE"
    fi
    echo ""
    
    # Backup obecnego pliku
    echo -e "${GREEN}💾 Tworzę backup...${NC}"
    cp "$STATE_FILE" "$BACKUP_FILE"
    echo "   ✓ Backup zapisany: $BACKUP_FILE"
    echo ""
else
    echo -e "${YELLOW}ℹ️  Plik state nie istnieje (to jest OK przy pierwszym uruchomieniu)${NC}"
    echo ""
fi

# Utwórz nowy plik state z datą 18 listopada 2025 00:00:00
NEW_TIMESTAMP="${TARGET_DATE}T00:00:00.000000"

echo -e "${GREEN}🔄 Resetuję pamięć do:${NC} $NEW_TIMESTAMP"
echo ""

# Zapisz nowy state
cat > "$STATE_FILE" << EOF
{
  "last_sync": "$NEW_TIMESTAMP"
}
EOF

echo -e "${GREEN}✓ Gotowe!${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Co dalej:${NC}"
echo ""
echo "1. Przy następnym uruchomieniu, system zobaczy wszystkie pliki"
echo "   audio z recordera utworzone PO: $TARGET_DATE 00:00:00"
echo ""
echo "2. Uruchom transkrypcję standardowo:"
echo "   ${YELLOW}python -m src.main${NC}"
echo ""
echo "3. Jeśli chcesz wrócić do poprzedniego stanu:"
echo "   ${YELLOW}mv $BACKUP_FILE $STATE_FILE${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"

