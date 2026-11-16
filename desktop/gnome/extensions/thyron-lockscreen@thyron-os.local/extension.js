// THYRON Lock Screen - GNOME Shell 50
//
// Escrita a partir do js/ui/unlockDialog.js da tag 50.5 do GNOME Shell.
// Regra de seguranca: so mexe no visual. A autenticacao (AuthPrompt, PAM,
// GDM) nao e tocada. Qualquer falha cai de volta no bloqueio padrao.

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';

import {Extension, InjectionManager} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as AuthPrompt from 'resource:///org/gnome/shell/gdm/authPrompt.js';
import * as UnlockDialog from 'resource:///org/gnome/shell/ui/unlockDialog.js';

// Posicao da coluna de login (fracoes da tela), conforme o mockup
const COLUMN_CENTER = 0.735;
const COLUMN_MIN_WIDTH = 0.30;
const LOGO_TOP = 0.05;
const STACK_TOP = 0.30;
const FOOTER_RESERVE = 0.09;

const SLOGAN = 'LIBERDADE  •  DESEMPENHO  •  INOVAÇÃO';
const HINT = 'Clique ou pressione uma tecla para desbloquear';

function ptDate() {
    const text = new Date().toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    });
    return text.charAt(0).toUpperCase() + text.slice(1);
}

const ThyronUnlockLayout = GObject.registerClass(
class ThyronUnlockLayout extends Clutter.LayoutManager {
    _init(stack, notifications, switchUserButton, logo, slogan) {
        super._init();

        this._stack = stack;
        this._notifications = notifications;
        this._switchUserButton = switchUserButton;
        this._logo = logo;
        this._slogan = slogan;
    }

    vfunc_get_preferred_width(container, forHeight) {
        return this._stack.get_preferred_width(forHeight);
    }

    vfunc_get_preferred_height(container, forWidth) {
        return this._stack.get_preferred_height(forWidth);
    }

    vfunc_allocate(container, box) {
        const [width, height] = box.get_size();
        const footerReserve = Math.floor(height * FOOTER_RESERVE);

        const [, , stackWidth, stackHeight] =
            this._stack.get_preferred_size();
        const [, , notifWidth, notifHeight] =
            this._notifications.get_preferred_size();

        const columnWidth = Math.max(
            stackWidth, notifWidth, Math.floor(width * COLUMN_MIN_WIDTH));
        const centerX = Math.floor(width * COLUMN_CENTER);
        const columnX1 = Math.floor(centerX - columnWidth / 2);

        const actorBox = new Clutter.ActorBox();

        // Logo (topo da coluna)
        const [, , logoWidth, logoHeight] = this._logo.get_preferred_size();
        actorBox.x1 = Math.floor(centerX - logoWidth / 2);
        actorBox.y1 = Math.floor(height * LOGO_TOP);
        actorBox.x2 = actorBox.x1 + logoWidth;
        actorBox.y2 = actorBox.y1 + logoHeight;
        this._logo.allocate(actorBox);

        // Notificacoes (base da coluna, acima do rodape)
        const maxNotifHeight = Math.max(0, Math.min(
            notifHeight,
            height - footerReserve - Math.floor(height / 10) - stackHeight));

        actorBox.x1 = columnX1;
        actorBox.y1 = height - footerReserve - maxNotifHeight;
        actorBox.x2 = columnX1 + columnWidth;
        actorBox.y2 = actorBox.y1 + maxNotifHeight;
        this._notifications.allocate(actorBox);

        // Relogio / autenticacao
        const stackY = Math.max(0, Math.min(
            Math.floor(height * STACK_TOP),
            height - footerReserve - stackHeight - maxNotifHeight));

        actorBox.x1 = columnX1;
        actorBox.y1 = stackY;
        actorBox.x2 = columnX1 + columnWidth;
        actorBox.y2 = stackY + stackHeight;
        this._stack.allocate(actorBox);

        // Slogan (rodape, a esquerda)
        const [, , sloganWidth, sloganHeight] = this._slogan.get_preferred_size();
        actorBox.x1 = Math.floor(width * 0.06);
        actorBox.y1 = Math.floor(height - footerReserve / 2 - sloganHeight / 2);
        // folga extra: o espacamento entre letras nao entra na medida do texto
        actorBox.x2 = actorBox.x1 + sloganWidth + 60;
        actorBox.y2 = actorBox.y1 + sloganHeight;
        this._slogan.allocate(actorBox);

        // Botao "trocar de usuario" (igual ao original)
        if (this._switchUserButton.visible) {
            const [, , natWidth, natHeight] =
                this._switchUserButton.get_preferred_size();

            const textDirection = this._switchUserButton.get_text_direction();
            if (textDirection === Clutter.TextDirection.RTL)
                actorBox.x1 = box.x1 + natWidth;
            else
                actorBox.x1 = box.x2 - (natWidth * 2);

            actorBox.y1 = box.y2 - (natHeight * 2);
            actorBox.x2 = actorBox.x1 + natWidth;
            actorBox.y2 = actorBox.y1 + natHeight;

            this._switchUserButton.allocate(actorBox);
        }
    }
});

// Aplica o visual THYRON a um UnlockDialog recem-criado. Cada etapa tem seu
// proprio try/catch: se uma falhar, o restante do dialogo continua padrao.
function decorate(dialog) {
    // 1) Textos em portugues no relogio
    try {
        const clock = dialog._clock;
        const updateDate = () => {
            clock._date.text = ptDate();
        };
        clock._wallClock.connect('notify::clock', updateDate);
        updateDate();
        clock._hint.text = HINT;
    } catch (e) {
        console.error(`[THYRON lockscreen] relogio: ${e.message}`);
    }

    // 2) Layout: coluna a direita + logo + slogan
    try {
        const stack = dialog._stack;
        const mainBox = dialog.get_children().find(
            c => c !== dialog._backgroundGroup && c.get_children().includes(stack));
        if (!mainBox)
            throw new Error('caixa principal nao encontrada');

        const logo = new St.Widget({style_class: 'thyron-lock-logo'});
        const slogan = new St.Label({
            text: SLOGAN,
            style_class: 'thyron-lock-slogan',
        });
        slogan.clutter_text.set_ellipsize(0); // Pango.EllipsizeMode.NONE

        const layout = new ThyronUnlockLayout(
            stack,
            dialog._notificationsBox,
            dialog._otherUserButton,
            logo,
            slogan);

        mainBox.add_child(logo);
        mainBox.add_child(slogan);
        mainBox.layout_manager = layout;

        // O avatar (dragao do Kali) e trocado pela logo THYRON quando o campo
        // de senha aparece. Para nao duplicar a logo, a do topo some em
        // fade enquanto a pagina de senha esta visivel (value: 0 = relogio,
        // 1 = senha).
        const syncTopLogo = () => {
            const v = Math.max(0, Math.min(1, dialog._adjustment.value));
            logo.opacity = Math.round(255 * (1 - v));
        };
        dialog._adjustment.connectObject('notify::value', syncTopLogo, dialog);
        syncTopLogo();
    } catch (e) {
        console.error(`[THYRON lockscreen] layout: ${e.message}`);
    }
}

export default class ThyronLockScreen extends Extension {
    enable() {
        this._injections = new InjectionManager();
        const proto = UnlockDialog.UnlockDialog.prototype;

        // Fundo nitido: desliga o desfoque fixo (brilho 0.65 / raio 90)
        this._injections.overrideMethod(proto, '_updateBackgroundEffects',
            () => function () {
                for (const widget of this._backgroundGroup) {
                    const effect = widget.get_effect('blur');
                    if (effect)
                        effect.enabled = false;
                }
            });

        // Fundo proprio do bloqueio (lobo a esquerda), independente do wallpaper
        // do desktop. Sem a imagem, mantem o fundo padrao do GNOME (sem desfoque).
        const lockBg = Gio.File.new_for_path(
            GLib.build_filenamev([this.path, 'assets', 'lock-wallpaper.png']));
        if (lockBg.query_exists(null)) {
            this._injections.overrideMethod(proto, '_createBackground',
                original => function (monitorIndex) {
                    try {
                        const monitor = Main.layoutManager.monitors[monitorIndex];
                        const widget = new St.Widget({
                            style_class: 'thyron-lock-background',
                            x: monitor.x,
                            y: monitor.y,
                            width: monitor.width,
                            height: monitor.height,
                        });
                        this._backgroundGroup.add_child(widget);
                    } catch (e) {
                        console.error(`[THYRON lockscreen] fundo: ${e.message}`);
                        original.call(this, monitorIndex);
                    }
                });
        }

        // Avatar do usuario (dragao do Kali) -> logo THYRON, no mesmo lugar.
        // O AuthPrompt do bloqueio recria o UserWidget a cada setUser(); aqui
        // o avatar original e apenas ocultado (nao destruido) e a logo entra
        // logo antes dele. O nome do usuario abaixo continua igual. Se algo
        // falhar, o avatar padrao permanece visivel.
        const logoPath = GLib.build_filenamev([this.path, 'assets', 'thyron-logo.png']);
        if (Gio.File.new_for_path(logoPath).query_exists(null)) {
            this._injections.overrideMethod(AuthPrompt.AuthPrompt.prototype, 'setUser',
                original => function (user) {
                    original.call(this, user);
                    try {
                        const userWidget = this._userWell?.get_child();
                        const avatar = userWidget?._avatar;
                        if (!avatar || userWidget._thyronLogo)
                            return;

                        const logo = new St.Widget({
                            style_class: 'thyron-lock-avatar-logo',
                            x_align: Clutter.ActorAlign.CENTER,
                        });
                        userWidget.insert_child_below(logo, avatar);
                        avatar.hide();
                        userWidget._thyronLogo = logo;
                    } catch (e) {
                        console.error(`[THYRON lockscreen] avatar: ${e.message}`);
                    }
                });
        }

        // Visual THYRON depois que o dialogo original foi construido
        this._injections.overrideMethod(proto, '_init',
            original => function (...args) {
                original.call(this, ...args);
                try {
                    decorate(this);
                } catch (e) {
                    console.error(`[THYRON lockscreen] ${e.message}\n${e.stack}`);
                }
            });
    }

    disable() {
        this._injections?.clear();
        this._injections = null;
    }
}
