#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFile>
#include <QHBoxLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QMainWindow>
#include <QProgressBar>
#include <QPushButton>
#include <QStackedWidget>
#include <QVBoxLayout>
#include <QDir>
#include <QStringList>
#include <QTimer>

class EosOobe final : public QMainWindow {
public:
    explicit EosOobe(const QString &root, QWidget *parent = nullptr) : QMainWindow(parent), root_(root) {
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
        languageSelect_ = new QComboBox(language);
        languageSelect_->addItems({"Español", "English", "Português", "Français"});
        languageLayout->addWidget(languageSelect_);
        languageLayout->addStretch();
        auto *privacy = new QWidget(stack);
        auto *privacyLayout = new QVBoxLayout(privacy);
        diagnostics_ = new QCheckBox("Permitir diagnósticos opcionales", privacy);
        localAssistant_ = new QCheckBox("Preparar el asistente local de EOS", privacy);
        localAssistant_->setChecked(true);
        privacyLayout->addWidget(diagnostics_);
        privacyLayout->addWidget(localAssistant_);
        privacyLayout->addStretch();
        auto *appearance = new QWidget(stack);
        auto *appearanceLayout = new QVBoxLayout(appearance);
        theme_ = new QComboBox(appearance);
        theme_->addItems({"Oscuro EOS", "Claro EOS", "Seguir preferencia del sistema"});
        appearanceLayout->addWidget(theme_);
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

        loadState(stack);
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
        connect(next, &QPushButton::clicked, this, [this, stack, update] {
            saveState(stack->currentIndex());
            if (stack->currentIndex() < stack->count() - 1) {
                stack->setCurrentIndex(stack->currentIndex() + 1);
                update();
            } else {
                saveState(3);
                close();
            }
        });
        connect(back, &QPushButton::clicked, this, [stack, update] {
            if (stack->currentIndex() > 0) {
                stack->setCurrentIndex(stack->currentIndex() - 1);
                update();
            }
        });
        connect(skip, &QPushButton::clicked, this, [this, stack] {
            saveState(stack->currentIndex(), true);
            close();
        });
        update();
    }

    void runSelfTest() {
        saveState(1);
        close();
    }

private:
    void loadState(QStackedWidget *stack) {
        QFile file(statePath());
        if (!file.open(QIODevice::ReadOnly)) return;
        const auto document = QJsonDocument::fromJson(file.readAll());
        if (!document.isObject()) return;
        const auto state = document.object();
        languageSelect_->setCurrentText(state.value("locale").toString("Español"));
        diagnostics_->setChecked(state.value("diagnostics").toBool(false));
        localAssistant_->setChecked(state.value("local_assistant").toBool(true));
        theme_->setCurrentText(state.value("theme").toString("Oscuro EOS"));
        const int completed = state.value("completed_steps").toInt(0);
        stack->setCurrentIndex(completed >= 3 ? 0 : qBound(0, completed, 2));
    }

    void saveState(int completedSteps, bool skipped = false) {
        QDir().mkpath(root_);
        QJsonObject state;
        state.insert("schema", "eos-oobe-0.2");
        state.insert("completed_steps", completedSteps);
        state.insert("skipped", skipped);
        state.insert("locale", languageSelect_->currentText());
        state.insert("diagnostics", diagnostics_->isChecked());
        state.insert("local_assistant", localAssistant_->isChecked());
        state.insert("theme", theme_->currentText());
        state.insert("next", completedSteps >= 3 ? "eos-phone-shell" : "eos-oobe");
        QFile file(statePath() + ".tmp");
        if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate)) return;
        file.write(QJsonDocument(state).toJson(QJsonDocument::Indented));
        file.close();
        QFile::remove(statePath());
        QFile::rename(statePath() + ".tmp", statePath());
    }

    QString statePath() const { return QDir(root_).filePath("oobe-state.json"); }
    QString root_;
    QComboBox *languageSelect_ = nullptr;
    QCheckBox *diagnostics_ = nullptr;
    QCheckBox *localAssistant_ = nullptr;
    QComboBox *theme_ = nullptr;
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    QString root = QDir::temp().filePath("eos-oobe-dev");
    bool selfTest = false;
    QString capturePath;
    for (int i = 1; i < argc; ++i) {
        if (QString(argv[i]) == "--self-test") selfTest = true;
        if (i + 1 < argc && QString(argv[i]) == "--root") root = QString(argv[i + 1]);
        if (i + 1 < argc && QString(argv[i]) == "--capture") capturePath = QString(argv[i + 1]);
    }
    EosOobe oobe(root);
    oobe.show();
    if (selfTest) QTimer::singleShot(0, &oobe, [&oobe] { oobe.runSelfTest(); });
    if (!capturePath.isEmpty()) QTimer::singleShot(250, &oobe, [&oobe, &app, capturePath] { oobe.grab().save(capturePath, "PNG"); app.quit(); });
    return app.exec();
}
