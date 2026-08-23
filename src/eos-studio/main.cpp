#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QFrame>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QTimer>
#include <QSplitter>
#include <QStackedWidget>
#include <QStatusBar>
#include <QTabWidget>
#include <QToolBar>
#include <QVBoxLayout>
#include <QWidget>

class StudioWindow final : public QMainWindow {
public:
    StudioWindow() {
        setWindowTitle("EOS Studio — Visual App Builder");
        resize(1280, 780);
        auto *toolbar = addToolBar("Project");
        auto *newActivity = toolbar->addAction("Nueva actividad");
        auto *preview = toolbar->addAction("Preview");
        auto *build = toolbar->addAction("Compilar .eapp");
        statusBar()->showMessage("Proyecto EOS: sin cambios");

        auto *root = new QSplitter(Qt::Horizontal, this);
        root->addWidget(projectPanel());
        root->addWidget(editorPanel());
        root->addWidget(inspectorPanel());
        root->setStretchFactor(0, 1);
        root->setStretchFactor(1, 4);
        root->setStretchFactor(2, 1);
        setCentralWidget(root);

        connect(newActivity, &QAction::triggered, this, [this] {
            activityList_->addItem("app.new_activity");
            activityList_->setCurrentRow(activityList_->count() - 1);
            statusBar()->showMessage("Actividad creada; edita su ruta y layout en el inspector");
        });
        connect(preview, &QAction::triggered, this, [this] {
            console_->appendPlainText("[preview] eos-activityd launch " + activityList_->currentItem()->text());
            console_->appendPlainText("[preview] lifecycle=created → started → resumed");
            console_->appendPlainText("[preview] touch/swipe routed to active activity");
            statusBar()->showMessage("Preview EOS ejecutado en runtime aislado");
        });
        connect(build, &QAction::triggered, this, [this] {
            console_->appendPlainText("[build] eoslangc → EOSBC 2");
            console_->appendPlainText("[build] eos-ui-check → PASS");
            console_->appendPlainText("[build] eos-triggerc → PASS");
            console_->appendPlainText("[build] eapp → manifest JSON + policy YAML + MF");
            statusBar()->showMessage("Build preparado; firma externa requerida para distribución");
        });
    }

private:
    QWidget *projectPanel() {
        auto *panel = new QWidget;
        auto *layout = new QVBoxLayout(panel);
        auto *title = new QLabel("PROYECTO EOS");
        title->setStyleSheet("font-weight: 700; color: #6ea8fe;");
        layout->addWidget(title);
        auto *tree = new QListWidget;
        tree->addItems({"eapp.json", "src/main.elang", "ui/", "styles/", "animations/", "policy/", "resources/"});
        tree->setObjectName("projectTree");
        layout->addWidget(tree);
        auto *activityTitle = new QLabel("ACTIVIDADES");
        activityTitle->setStyleSheet("font-weight: 700; color: #6ea8fe;");
        layout->addWidget(activityTitle);
        activityList_ = new QListWidget;
        activityList_->addItems({"app.home", "app.settings"});
        layout->addWidget(activityList_);
        connect(activityList_, &QListWidget::currentRowChanged, this, [this](int row) {
            if (row >= 0) {
                activityLabel_->setText(activityList_->item(row)->text());
                statusBar()->showMessage("Editando actividad " + activityList_->item(row)->text());
            }
        });
        return panel;
    }

    QWidget *editorPanel() {
        auto *panel = new QWidget;
        auto *layout = new QVBoxLayout(panel);
        auto *activityBar = new QHBoxLayout;
        activityLabel_ = new QLabel("app.home");
        activityLabel_->setStyleSheet("font-size: 18px; font-weight: 700;");
        activityBar->addWidget(activityLabel_);
        auto *mode = new QComboBox;
        mode->addItems({"Diseño", "Código", "Triggers", "Animaciones"});
        activityBar->addStretch();
        activityBar->addWidget(new QLabel("Modo:"));
        activityBar->addWidget(mode);
        layout->addLayout(activityBar);

        tabs_ = new QTabWidget;
        tabs_->addTab(designCanvas(), "Canvas");
        auto *code = new QPlainTextEdit;
        code->setPlainText("fn on_home_create() -> void\n  call ui.show \\\"app.home\\\"\nendfn\n");
        code->setPlaceholderText("Escribe EosLang aquí…");
        tabs_->addTab(code, "EosLang");
        auto *triggers = new QPlainTextEdit;
        triggers->setPlainText("schema: eos-triggers-0.2\ntriggers:\n  - id: gesture.swipe-left\n    activity: app.home\n    handler: on_swipe_left\n    delivery: resumed-only\n");
        tabs_->addTab(triggers, "Triggers YAML");
        auto *styles = new QPlainTextEdit;
        styles->setPlainText("@activity app.home {\n  background: eos.surface;\n  touch-target: comfortable;\n  safe-area: avoid;\n}\n");
        tabs_->addTab(styles, "EOS CSS");
        layout->addWidget(tabs_);
        console_ = new QPlainTextEdit;
        console_->setReadOnly(true);
        console_->setMaximumHeight(130);
        console_->setPlainText("[studio] Preview y depuración listos\n");
        layout->addWidget(console_);
        return panel;
    }

    QWidget *designCanvas() {
        auto *canvas = new QFrame;
        canvas->setFrameShape(QFrame::StyledPanel);
        canvas->setStyleSheet("QFrame { background: #101522; border: 1px solid #36425d; } QPushButton { background: #314f89; color: white; padding: 10px; border-radius: 6px; } QLabel { color: #f6f8ff; }");
        auto *layout = new QVBoxLayout(canvas);
        auto *safe = new QLabel("SAFE AREA • EOS UI • 1080×2400");
        safe->setAlignment(Qt::AlignCenter);
        layout->addWidget(safe);
        auto *bar = new QLabel("Notas");
        bar->setStyleSheet("font-size: 20px; font-weight: 700; padding: 12px;");
        layout->addWidget(bar);
        auto *editor = new QPlainTextEdit;
        editor->setPlaceholderText("Selecciona un control para editarlo en el inspector");
        editor->setObjectName("previewEditor");
        layout->addWidget(editor);
        auto *save = new QPushButton("Guardar");
        layout->addWidget(save);
        auto *hint = new QLabel("Arrastra controles desde la paleta • conecta acciones y gestos desde Triggers");
        hint->setAlignment(Qt::AlignCenter);
        layout->addWidget(hint);
        return canvas;
    }

    QWidget *inspectorPanel() {
        auto *panel = new QWidget;
        auto *layout = new QVBoxLayout(panel);
        auto *title = new QLabel("INSPECTOR");
        title->setStyleSheet("font-weight: 700; color: #6ea8fe;");
        layout->addWidget(title);
        auto *controls = new QListWidget;
        controls->addItems({"AppBar", "TextInput", "Button", "List", "Image", "Navigation"});
        layout->addWidget(new QLabel("PALETA DE CONTROLES"));
        layout->addWidget(controls);
        auto *group = new QGroupBox("Propiedades EOS UI");
        auto *form = new QFormLayout(group);
        form->addRow("id", new QLineEdit("save"));
        form->addRow("type", new QLineEdit("button"));
        form->addRow("action", new QLineEdit("save_note"));
        form->addRow("touch-target", new QComboBox);
        form->addRow("safe-area", new QCheckBox);
        layout->addWidget(group);
        layout->addStretch();
        return panel;
    }

    QListWidget *activityList_ = nullptr;
    QLabel *activityLabel_ = nullptr;
    QTabWidget *tabs_ = nullptr;
    QPlainTextEdit *console_ = nullptr;
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    StudioWindow window;
    window.show();
    QString capture_path;
    if (argc == 3 && QString::fromLocal8Bit(argv[1]) == "--capture") {
        capture_path = QString::fromLocal8Bit(argv[2]);
        QTimer::singleShot(250, &window, [&window, &app, capture_path] {
            window.grab().save(capture_path, "PNG");
            app.quit();
        });
    }
    return app.exec();
}
