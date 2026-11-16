# Changelog

Mudanças relevantes serão registradas aqui. O projeto ainda não possui uma versão distribuível.

## Unreleased

### Added
- Pacote `thyron-desktop` `0.1.0~dev1` (`packages/thyron-desktop/`): instala as extensões `thyron-app-launcher` e `thyron-lockscreen` em `/usr/share/gnome-shell/extensions/`, ativa-as por padrão via `/etc/dconf/db/local.d/10-thyron-desktop` e instala os wallpapers em `/usr/share/backgrounds/thyron/`. Build interno (licença dos ativos pendente). Cobertura: `tests/integration/test_thyron_desktop_package.py`. Instalação real na VM ainda não testada.
- Imagens conceituais de logotipo, wallpapers e mockups de referência em `branding/` (autoria/licença pendentes; ver `branding/ASSETS.md`).
- Estrutura inicial do repositório.
- Documentação de arquitetura, decisões, roadmap, testes e primeira ISO.
- Modelos de Issues e Pull Requests.
- Workflow inicial de validação documental.
