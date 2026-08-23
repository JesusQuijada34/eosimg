#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QMainWindow>
#include <QProgressBar>
#include <QPushButton>
#include <QStackedWidget>
#include <QVBoxLayout>
#include <QWidget>

class EosOobe final : public QMainWindow {
public:
    EosOobe() {
        setWindowTitle("Etternhall Operating System — Setup");
        resize(760, 520);
        setStyleSheet(R"(
            QMainWindow, QWidget { background: #101522; color: #f6f8ff; }
            QLabel#eyebrow { color: #8ea6d5; font-size: 13px; }
            QLabel#title { font-size: 30px; font-weight: 700; }
            QLabel#body { color: #c2cbe0; font-size: 15px; }
            QComboBox, QCheckBox { background: #1b263b; border: 1px solid #34496d; border-radius: 8px; padding: 12px; min-height: 24px; }
            QPushButton { border-radius: 8px; padding: 12px 22px; min-width: 110px; }
            QPushButton#primary { background: #4f7ecf; color: white; border: 1px solid #6e9bea; }
            QPushButton#secondary { background: transparent; color: #d9e3f8; border: 1px solid #48628f; }
            QProgressBar { border: none; background: #202c42; height: 6px; border-radius: 3px; }
            QProgressBar::chunk { background: #6e9bea; border-radius: 3px; }
        )");

        auto *page = new QWidget(this);
        auto *main = new QVBoxLayout(page);
        main->setContentsMargins(64, 42, 64, 32);
        main->setSpacing(18);
        auto *eyebrow = new QLabel("ETTERNHALL OPERATING SYSTEM", page);
        eyebrow->setObjectName("eyebrow");
        main->addWidget(eyebrow);
        auto *title = new QLabel(page);
        title->setObjectName("title");
        main->addWidget(title);
        auto *body = new QLabel(page);
        body->setObjectName("body");
        body->setWordWrap(true);
        main->addWidget(body);
        auto *stack = new QStackedWidget(page);
        auto *language = new QWidget(stack);
        auto *languageLayout = new QVBoxLayout(language);
        auto *languageSelect = new QComboBox(language);
        languageSelect->addItems({"Español", "English", "Português", "Français"});
        languageLayout->addWidget(languageSelect);
        languageLayout->addStretch();
        auto *privacy = new QWidget(stack);
        auto *privacyLayout = new QVBoxLayout(privacy);
        auto *diagnostics = new QCheckBox("Permitir diagnósticos opcionales", privacy);
        auto *localAssistant = new QCheckBox("Preparar el asistente local de EOS", privacy);
        localAssistant->setChecked(true);
        privacyLayout->addWidget(diagnostics);
        privacyLayout->addWidget(localAssistant);
        privacyLayout->addStretch();
        auto *appearance = new QWidget(stack);
        auto *appearanceLayout = new QVBoxLayout(appearance);
        auto *theme = new QComboBox(appearance);
        theme->addItems({"Oscuro EOS", "Claro EOS", "Seguir preferencia del sistema"});
        appearanceLayout->addWidget(theme);
        appearanceLayout->addStretch();
        stack->addWidget(language);
        stack->addWidget(privacy);
        stack->addWidget(appearance);
        main->addWidget(stack, 1);
        auto *progress = new QProgressBar(page);
        progress->setRange(0, 2);
        progress->setValue(0);
        progress->setTextVisible(false);
        main->addWidget(progress);
        auto *actions = new QHBoxLayout();
        auto *back = new QPushButton("Atrás", page);
        back->setObjectName("secondary");
        auto *skip = new QPushButton("Omitir", page);
        skip->setObjectName("secondary");
        auto *next = new QPushButton("Continuar", page);
        next->setObjectName("primary");
        actions->addWidget(back);
        actions->addStretch();
        actions->addWidget(skip);
        actions->addWidget(next);
        main->addLayout(actions);
        setCentralWidget(page);

        const auto update = [stack, title, body, progress, back, next] {
            const int step = stack->currentIndex();
            const QStringList titles = {"Bienvenido a EOS", "Tu privacidad primero", "Elige tu apariencia"};
            const QStringList bodies = {"Vamos a preparar tu dispositivo con unos pasos sencillos.", "Decide qué funciones opcionales estarán disponibles para EOS.", "Puedes cambiar estas preferencias más tarde desde eJairo."};
            title->setText(titles.at(step));
            body->setText(bodies.at(step));
            progress->setValue(step);
            back->setEnabled(step > 0);
            next->setText(step == 2 ? "Terminar" : "Continuar");
        };
        connect(next, &QPushButton::clicked, this, [stack, update] {
            if (stack->currentIndex() < stack->count() - 1) stack->setCurrentIndex(stack->currentIndex() + 1);
            else QApplication::quit();
            update();
        });
        connect(back, &QPushButton::clicked, this, [stack, update] {
            if (stack->currentIndex() > 0) stack->setCurrentIndex(stack->currentIndex() - 1);
            update();
        });
        connect(skip, &QPushButton::clicked, this, [this] { close(); });
        update();
    }
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    EosOobe oobe;
    oobe.show();
    return app.exec();
}
