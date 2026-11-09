# Plano da primeira ISO Live

## Objetivo

Produzir uma ISO **experimental e somente para avaliação Live**, baseada no Kali Live Build, para validar a cadeia de build, o boot e a sessão GNOME personalizada. Não é uma versão estável nem uma recomendação de instalação em computador principal.

## Escopo mínimo

- Base Kali oficial e versão/snapshot registrados.
- GNOME como desktop.
- Seleção enxuta de pacotes.
- Branding THYRON básico (wallpaper, metadados e tema inicial, quando os ativos estiverem prontos).
- Configuração de boot Live.
- Sem instalador personalizado no primeiro ciclo.
- Sem alterações automáticas no disco do usuário.

## Fora de escopo

- THYRON Store funcional.
- Style Center completo.
- Customização profunda de GDM.
- Promessa de suporte a todo hardware.
- Instalação em máquina física como primeiro teste.

## Pré-requisitos a confirmar

Antes de instalar ferramentas de build, registrar:
- distribuição e versão do host;
- arquitetura;
- CPU e núcleos;
- RAM;
- espaço livre e filesystem;
- Git e Python;
- virtualização disponível (KVM/QEMU ou alternativa).

Não assumir a distribuição hospedeira. O computador do desenvolvedor deve permanecer intacto.

## Estratégia técnica

1. Consultar a documentação oficial atual do Kali Live Build.
2. Fixar a referência de build (release/branch/commit) usada no experimento.
3. Manter configuração THYRON em `iso/kali-config/`.
4. Separar listas de pacotes por perfil, sem instalar coleções enormes por padrão.
5. Usar includes/hooks apenas quando necessários e documentados.
6. Construir em ambiente compatível e isolado, preferencialmente VM ou ambiente de build dedicado.
7. Armazenar logs, manifesto de pacotes, hash SHA-256 e versão da configuração junto aos artefatos de release.
8. Não versionar a ISO no Git; publicar artefatos de teste em GitHub Releases quando apropriado.

## Estrutura de configuração proposta

```text
iso/
├── README.md
└── kali-config/
    ├── package-lists/
    │   └── thyron.list.chroot
    ├── includes.chroot/
    │   └── etc/
    │       └── thyron/
    ├── hooks/
    └── build-notes.md
```

Os diretórios de hooks/includes podem permanecer vazios até haver necessidade concreta. Não adicionar scripts de build sem validar o ambiente e a documentação correspondente.

## Sequência do primeiro build

### Fase A — Preparação
- [ ] Diagnóstico do host registrado.
- [ ] Espaço de armazenamento verificado.
- [ ] Documentação oficial do Kali consultada.
- [ ] Versão/commit do sistema de build fixada.
- [ ] Lista de pacotes revisada.

### Fase B — Configuração
- [ ] Variante GNOME confirmada.
- [ ] Configuração de branding incluída.
- [ ] Pacotes mínimos definidos.
- [ ] Hooks revisados e justificados.
- [ ] Licenças dos ativos conferidas.

### Fase C — Construção
- [ ] Build executado em ambiente compatível.
- [ ] Log preservado.
- [ ] Manifesto de pacotes gerado.
- [ ] Hash SHA-256 gerado.
- [ ] Nenhum artefato binário adicionado ao Git.

### Fase D — Testes em VM
- [ ] ISO inicia.
- [ ] Sessão Live abre.
- [ ] GNOME inicia sem falhas críticas.
- [ ] Teclado e resolução funcionam.
- [ ] Rede funciona.
- [ ] Áudio é verificado quando suportado pela VM.
- [ ] Aplicativos essenciais abrem.
- [ ] Suspensão/retomada é avaliada quando suportada.
- [ ] Encerramento funciona.
- [ ] Uso de RAM/CPU registrado.

## Critérios de aprovação

A ISO só pode ser marcada como **experimental testada** se os testes mínimos de boot, sessão, rede e encerramento passarem em uma VM identificada, com log e hash arquivados. Falhas e limitações devem constar nas notas de versão.

## Recuperação e segurança

- Não testar inicialmente no disco principal.
- Não gravar a ISO em USB com dados importantes.
- Não executar scripts com `sudo` sem revisão.
- Não modificar GRUB, repositórios ou serviços do host para facilitar o build.
- Se a VM falhar, preservar log e configuração; corrigir em branch e repetir os testes.

## Referências oficiais para consultar durante a implementação

- Kali Live Build: https://www.kali.org/docs/development/live-build-a-custom-kali-iso/
- Kali build scripts: https://gitlab.com/kalilinux/build-scripts/kali-live
- Kali metapackages: https://www.kali.org/docs/general-use/metapackages/
