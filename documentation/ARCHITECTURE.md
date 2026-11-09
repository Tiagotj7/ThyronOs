# Arquitetura do THYRON OS

## Princípios

- Modularidade: identidade, experiência desktop, aplicativos e imagem do sistema são camadas separadas.
- Compatibilidade: GNOME é a plataforma desktop principal; validar cada extensão contra a versão-alvo.
- Reversibilidade: alterações de configuração devem permitir restauração.
- Segurança: preservar mecanismos de autenticação e atualização da base Kali.
- Transparência: distinguir planejado, implementado e testado.

## Camadas

```text
THYRON Experience
  ├── Branding & Themes
  ├── GNOME Shell Extensions
  ├── Style Center / Store / Utilities
  └── Terminal Profile
          |
THYRON Core
  ├── Profiles and settings
  ├── Configuration defaults
  ├── Recovery / diagnostics
  └── Package integration
          |
GNOME Platform
  ├── GNOME Shell / Mutter / GDM
  ├── GTK / GJS
  └── GSettings / dconf
          |
Kali Linux / Debian infrastructure
  ├── APT / dpkg
  ├── Kali repositories
  └── Live Build
```

## Linguagens e tecnologias previstas

| Área | Tecnologia proposta | Observação |
|---|---|---|
| Extensões GNOME | GJS / JavaScript | Seguir o formato de módulos da versão GNOME escolhida |
| Aplicativos GTK | Python + PyGObject ou GJS | Escolher por aplicativo; evitar duas stacks sem necessidade |
| Estilos | CSS, GTK CSS e recursos GNOME suportados | Não depender de hacks frágeis |
| Configuração e build | Bash, YAML, Python | Scripts pequenos, auditáveis e idempotentes quando possível |
| Empacotamento | Debian packaging | Pacotes separados quando a divisão estiver madura |
| Imagem | Kali Live Build | Configuração versionada no diretório `iso/` |
| Testes | pytest / shellcheck / testes manuais | Adicionar conforme código real surgir |

## Organização dos diretórios

- `branding/`: logotipo, mascote, wallpapers, ícones, fontes e respectivas licenças.
- `core/`: esquemas, perfis, serviços, recuperação e diagnóstico.
- `desktop/gnome/`: extensões e integração com Shell.
- `desktop/gdm/`: personalizações avaliadas para GDM, sempre com rollback.
- `applications/`: aplicativos THYRON independentes.
- `themes/`: seis perfis visuais.
- `terminal/`: perfil do GNOME Terminal e configuração ZSH.
- `packages/`: metadados e receitas de pacotes Debian.
- `iso/`: configuração Kali Live Build e listas de pacotes.
- `installer/`: pesquisa técnica; sem instalador próprio no primeiro marco.
- `scripts/`: ferramentas auxiliares de desenvolvimento.
- `tests/`: testes automatizados e checklists de VM.
- `documentation/`: decisões, roadmap, procedimentos e registros.

## Dependências e limites

A primeira ISO deve começar com um conjunto pequeno de pacotes. Ferramentas Kali adicionais serão opcionais ou agrupadas em perfis, evitando uma imagem excessiva. A integração APT/Flatpak deverá usar ferramentas oficiais e operações explícitas do usuário.

A personalização do GDM e da tela de bloqueio é sensível à versão e pode afetar o acesso. Ela não deve bloquear a primeira ISO experimental; deve entrar apenas após um método de recuperação testado.

## Estados de implementação

Use estes estados nos documentos e Issues:
- **Planejado**: ideia aprovada, ainda sem código.
- **Em desenvolvimento**: existe implementação em branch.
- **Implementado**: código integrado.
- **Testado**: critérios definidos passaram em ambiente identificado.
- **Bloqueado**: depende de decisão ou correção externa.

Nenhum item deve ser chamado de testado sem registrar versão, ambiente e resultado.
