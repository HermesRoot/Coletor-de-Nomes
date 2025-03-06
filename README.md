# File Name Collector

**File Name Collector** é uma aplicação desktop desenvolvida em **Python** com **wxPython** que permite coletar e salvar a lista de nomes de arquivos (e opcionalmente pastas) de uma diretoria.

## 🖥️ Captura de Tela
![Screenshot do Coletor-de-Nomes](https://raw.githubusercontent.com/HermesRoot/Coletor-de-Nomes/refs/heads/main/screenshot.jpg)

## ✨ Recursos

- Coleta nomes de arquivos de uma pasta selecionada.
- Filtro por extensões específicas (ex: `.txt, .jpg`).
- Inclusão opcional de subpastas.
- Inclusão opcional de nomes de pastas no resultado.
- Salvamento da lista em arquivo `.txt`.
- Interface gráfica amigável.
- Suporte a múltiplos idiomas (`pt_BR` e `en_US`).
- Configuração persistente via `config.json`.

## 🛠️ Instalação

1. **Clone o repositório**:
    ```bash
    git clone https://github.com/HermesRoot/Coletor-de-Nomes.git
    cd file-name-collector
    ```

2. **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Execute o programa**:
    ```bash
    python coletor-de-nomes.py
    ```

## 📂 Como usar

1. Clique em **"Scan Folder"** para selecionar a pasta desejada.
2. (Opcional) Defina as extensões para filtrar os arquivos (ex: `.txt, .jpg`).
3. Marque **"Include Subfolders"** se quiser incluir subpastas.
4. Marque **"Include Folder Names"** para incluir também os nomes das pastas.
5. Escolha onde deseja salvar a lista gerada.
6. Veja os resultados na tela e no arquivo gerado.

## ⚙️ Configurações

As preferências são salvas no arquivo `config.json`, incluindo:

- Extensões padrão.
- Último diretório salvo.
- Idioma selecionado.
- Diretório padrão de salvamento.

## 🌐 Idiomas

O programa suporta os seguintes idiomas:

- 🇧🇷 Português (pt_BR)
- 🇺🇸 English (en_US)

Os arquivos de tradução `.mo` devem estar organizados da seguinte forma:
locale/ ├── pt_BR/ │ └── pt_BR.mo └── en_US/ └── en_US.mo

Você pode alternar o idioma pelo menu:  
`Settings -> Language -> [Português | English]`

## 📝 Licença

Este projeto está licenciado sob a licença **MIT** — veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👤 Autor

Desenvolvido por **HermesRoot**.  


