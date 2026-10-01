# 🌵 Lampião Adventures: The Busca of The Catita

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pygame](https://img.shields.io/badge/Engine-Pygame--CE-green)
![Genre](https://img.shields.io/badge/Gênero-Plataforma%202D%20%7C%20Pixel%20Art-orange)

**Lampião Adventures: The Busca of The Catita** é um jogo de plataforma 2D retrô com temática nordestina e estética pixel art. O jogador assume o papel do destemido cangaceiro **Lampião** em sua perigosa jornada pela caatinga para resgatar sua amada **Catita**.

---

## 🎮 Controles

| Ação | Teclas Principais | Teclas Alternativas |
| :--- | :--- | :--- |
| **Mover para Esquerda** | `A` | Seta `←` |
| **Mover para Direita** | `D` | Seta `→` |
| **Pular** | `W` / `ESPAÇO` | Seta `↑` |
| **Correr (Pique)** | `SHIFT` Esquerdo | `SHIFT` Direito |
| **Atirar** | `F` / `J` | `K` / `CTRL` Esquerdo |
| **Direcionar Tiro** | Segurar `W` (Cima) / `S` (Baixo) | Segurar `↑` (Cima) / `↓` (Baixo) |
| **Interagir** | `E` | — |
| **Pausar** | `ESC` | `P` |
| **Tentar Novamente** | `R` *(na tela de Game Over)* | `ENTER` / `ESPAÇO` |

---

## 🤠 Personagens e NPCs

- **🌵 Lampião**: O protagonista valente do cangaço. Equipado com sua garrucha, possui barras de **Vida** e **Fôlego** (stamina).
- **🐷 Catita**: A amada de Lampião, localizada no final do mapa. Ao se aproximar dela e pressionar a tecla `E`, o resgate é efetuado e o jogo retorna ao Menu Principal.
- **🫏 Jegue do Sertão**: NPC amigável no início da caatinga que fornece dicas valiosas sobre a jornada e os comandos do jogo.
- **🙏 Bemzedor (Padre/Rezador)**: NPC santificado do sertão. Ao conversar com ele, ele realiza uma oração ritualística que recupera a vida do Lampião. Durante a reza, todo o mapa entra em pausa respeitosa para garantir a segurança do jogador.

---

## 👹 Inimigos e Perigos

- **🤠 Cangaceiro Caçador (Chaser Enemy)**: Inimigo terrestre que patrulha a caatinga e persegue o Lampião ao avistá-lo.
- **🐝 Tanajura Voadora (Tanajura Enemy)**: Inimigo voador que cruza os céus do sertão em rotas de patrulha aérea.
- **🐂 Vaca Mojada (Boss / Perigo Ambiental)**: A lendária criatura do sertão. Surge no meio do mapa com uma cena de introdução marcante, mugido temível e investidas brutais pelo solo a cada 7 segundos.
- **🦅 Urubu do Pix**: Ameaça voadora recorrente nos céus do sertão.

---

## 🚀 Como Executar o Jogo

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.10** ou superior instalado em seu sistema.

### 2. Instalar Dependências
No terminal ou prompt de comando, navegue até a pasta do projeto e instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Iniciar o Jogo
Execute o arquivo principal para abrir o menu do jogo:

```bash
python main.py
```

---

## 📁 Estrutura do Projeto

```text
lampiaoadventures-main/
│
├── assets/                  # Sprites, tilesets, áudios e efeitos sonoros
│   ├── audio/               # Trilhas de fundo e SFX
│   └── sprites/             # Spritesheets de personagens, casas e cenários
│
├── src/                     # Código-fonte do jogo
│   ├── core/                # Motores de áudio, câmera, engine e gerenciador de cenas
│   ├── entities/            # Player, Inimigos, NPCs, Vaca Mojada, Catita e Tiros
│   ├── level/               # Gerenciador de níveis, tilemap parser e parallax
│   ├── scenes/              # Cenas de Menu, Gameplay e Cutscenes
│   ├── ui/                  # HUD, caixa de diálogo e transições
│   └── utils/               # Carregador de imagens e spritesheets
│
├── config.py                # Configurações globais (resolução, física, teclas, cores)
├── main.py                  # Ponto de entrada do jogo
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação oficial do projeto
```

---

## 🎨 Créditos e Licença

Desenvolvido para **Lampião Adventures**. Todos os direitos reservados.
