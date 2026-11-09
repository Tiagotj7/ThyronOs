# Contribuindo com o THYRON OS

Obrigado pelo interesse. O projeto está em fase inicial; contribuições pequenas, documentadas e verificáveis são preferíveis a grandes mudanças difíceis de revisar.

## Antes de começar

- Leia o README e `documentation/ARCHITECTURE.md`.
- Confira as decisões em `documentation/DECISIONS.md`.
- Verifique se já existe uma Issue relacionada.
- Não assuma que funcionalidades descritas no roadmap já existem.

## Fluxo recomendado

1. Abra ou comente uma Issue descrevendo problema, motivação e impacto.
2. Crie uma branch: `feat/nome-curto`, `fix/nome-curto` ou `docs/nome-curto`.
3. Faça uma alteração por Pull Request.
4. Execute os testes aplicáveis.
5. Atualize documentação, changelog e evidências quando necessário.
6. Descreva limitações conhecidas no Pull Request.

## Padrões

- Prefira alterações modulares e reversíveis.
- Não execute comandos privilegiados automaticamente em scripts.
- Não altere repositórios APT, GRUB, GDM ou configurações do hospedeiro sem justificativa, revisão e instruções de recuperação.
- Não inclua credenciais, tokens, chaves privadas, logs com dados pessoais ou imagens ISO no Git.
- Registre versões e compatibilidade de GNOME, Kali e dependências.
- Respeite licenças e atribuições de ativos de terceiros.

## Pull Requests

Inclua:
- objetivo e escopo;
- arquivos/componentes afetados;
- como testar;
- resultado observado;
- riscos e procedimento de reversão;
- capturas de tela, quando forem relevantes e não expuserem dados pessoais.

## Código de conduta

Mantenha comunicação respeitosa, inclusiva e focada em colaboração técnica. Críticas devem tratar do trabalho, não da pessoa.
