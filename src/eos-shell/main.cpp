#include <QApplication>
#include <QDateTime>
#include <QDialog>
#include <QFrame>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QPushButton>
#include <QPlainTextEdit>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>
#include <QVector>

class EosDesktop final : public QMainWindow {
public:
    EosDesktop() {
        setWindowTitle("Etternhall Desktop");
        resize(1280, 800);
        setMinimumSize(980, 640);
        setStyleSheet(R"(
            QMainWindow, QWidget { background: #0f1420; color: #eef3ff; font-family: "Noto Sans", sans-serif; }
            QFrame#panel { background: #172239; border-bottom: 1px solid #33496e; }
            QPushButton#brand { background: #4778c9; border: none; border-radius: 8px; padding: 8px 18px; font-weight: 700; }
            QPushButton#panelButton { background: transparent; border: none; padding: 8px 12px; color: #dce7ff; }
            QPushButton#panelButton:hover { background: #25385b; border-radius: 6px; }
            QLabel#clock { color: #c6d5f2; padding: 8px 14px; }
            QFrame#desktop { background: #111a2b; border: none; }
            QLabel#desktopTitle { font-size: 30px; font-weight: 700; color: #f5f8ff; }
            QLabel#desktopSubtitle { font-size: 14px; color: #9fb0d0; }
            QPushButton#tile { background: #223252; border: 1px solid #38527e; border-radius: 10px; padding: 16px; text-align: left; font-size: 14px; }
            QPushButton#tile:hover { background: #2c4671; border-color: #6c9ced; }
            QFrame#appWindow { background: #172239; border: 1px solid #5572a4; border-radius: 10px; }
            QFrame#appHeader { background: #213354; border-top-left-radius: 10px; border-top-right-radius: 10px; }
            QLabel#windowTitle { font-weight: 700; padding: 8px 12px; }
            QPushButton#windowButton { background: transparent; border: none; padding: 7px 10px; }
            QPushButton#windowButton:hover { background: #36517e; }
            QFrame#taskbar { background: #182640; border-top: 1px solid #33496e; }
            QPushButton#task { background: #263b62; border: 1px solid #3f5d8f; border-radius: 6px; padding: 6px 12px; }
            QPushButton#task:hover { background: #36517e; }
            QDialog { background: #172239; }
            QLineEdit, QListWidget, QPlainTextEdit { background: #111a2b; border: 1px solid #405b89; border-radius: 6px; color: #eef3ff; padding: 7px; }
        )");

        auto *root = new QWidget(this);
        auto *rootLayout = new QVBoxLayout(root);
        rootLayout->setContentsMargins(0, 0, 0, 0);
        rootLayout->setSpacing(0);
        rootLayout->addWidget(panel());
        workspace_ = new QFrame(root);
        workspace_->setObjectName("desktop");
        rootLayout->addWidget(workspace_, 1);
        rootLayout->addWidget(taskbar());
        setCentralWidget(root);

        addAppWindow("Archivos", 70, 120, 410, 300, "Tus archivos EOS\n\nEste espacio usa eos-storaged y roots lógicos.");
        addAppWindow("Notas", 520, 150, 420, 330, "Notas locales EOS\n\nActividad: notes.home\nSwipe o doble clic para abrir el editor.");
        updateClock();
    }

    void capture(const QString &path) {
        QTimer::singleShot(250, this, [this, path] { grab().save(path, "PNG"); qApp->quit(); });
    }

private:
    QWidget *panel() {
        auto *frame = new QFrame;
        frame->setObjectName("panel");
        frame->setFixedHeight(50);
        auto *layout = new QHBoxLayout(frame);
        layout->setContentsMargins(12, 5, 10, 5);
        auto *brand = new QPushButton("Etternhall", frame);
        brand->setObjectName("brand");
        layout->addWidget(brand);
        auto *launcher = new QPushButton("Aplicaciones", frame);
        launcher->setObjectName("panelButton");
        layout->addWidget(launcher);
        auto *search = new QPushButton("Buscar", frame);
        search->setObjectName("panelButton");
        layout->addWidget(search);
        auto *workspaces = new QPushButton("Escritorios  1  2  3", frame);
        workspaces->setObjectName("panelButton");
        layout->addWidget(workspaces);
        layout->addStretch();
        auto *status = new QLabel("Wi-Fi   Audio   Batería", frame);
        status->setObjectName("clock");
        layout->addWidget(status);
        clock_ = new QLabel(frame);
        clock_->setObjectName("clock");
        layout->addWidget(clock_);
        connect(brand, &QPushButton::clicked, this, [this] { showLauncher(); });
        connect(launcher, &QPushButton::clicked, this, [this] { showLauncher(); });
        connect(search, &QPushButton::clicked, this, [this] { addAppWindow("Buscar EOS", 270, 100, 500, 210, "Busca apps, archivos y ajustes desde el sistema EOS."); });
        return frame;
    }

    QWidget *taskbar() {
        auto *frame = new QFrame;
        frame->setObjectName("taskbar");
        frame->setFixedHeight(44);
        taskLayout_ = new QHBoxLayout(frame);
        taskLayout_->setContentsMargins(12, 5, 12, 5);
        auto *hint = new QLabel("Workspace 1  •  Ventanas EOS", frame);
        hint->setStyleSheet("color: #9fb0d0;");
        taskLayout_->addWidget(hint);
        taskLayout_->addStretch();
        return frame;
    }

    void showLauncher() {
        auto *dialog = new QDialog(this);
        dialog->setAttribute(Qt::WA_DeleteOnClose);
        dialog->setWindowTitle("Aplicaciones EOS");
        dialog->resize(520, 410);
        auto *layout = new QVBoxLayout(dialog);
        auto *title = new QLabel("Aplicaciones", dialog);
        title->setObjectName("desktopTitle");
        layout->addWidget(title);
        auto *search = new QLineEdit(dialog);
        search->setPlaceholderText("Buscar una aplicación EOS…");
        layout->addWidget(search);
        auto *list = new QListWidget(dialog);
        list->addItems({"Archivos", "Notas", "Ajustes", "EOS Studio", "EOS Browser", "Multimedia", "Marketplace"});
        layout->addWidget(list);
        connect(list, &QListWidget::itemDoubleClicked, dialog, [this, dialog](QListWidgetItem *item) {
            addAppWindow(item->text(), 180, 100, 440, 280, "Actividad principal EOS\n\nLa aplicación se ejecuta como .eapp firmado.");
            dialog->close();
        });
        dialog->show();
    }

    void addAppWindow(const QString &title, int x, int y, int width, int height, const QString &body) {
        auto *window = new QFrame(workspace_);
        window->setObjectName("appWindow");
        window->setGeometry(x, y, width, height);
        auto *root = new QVBoxLayout(window);
        root->setContentsMargins(0, 0, 0, 0);
        root->setSpacing(0);
        auto *header = new QFrame(window);
        header->setObjectName("appHeader");
        auto *headerLayout = new QHBoxLayout(header);
        headerLayout->setContentsMargins(6, 0, 4, 0);
        auto *label = new QLabel(title, header);
        label->setObjectName("windowTitle");
        headerLayout->addWidget(label);
        headerLayout->addStretch();
        auto *minimize = new QPushButton("—", header);
        minimize->setObjectName("windowButton");
        auto *maximize = new QPushButton("□", header);
        maximize->setObjectName("windowButton");
        auto *close = new QPushButton("×", header);
        close->setObjectName("windowButton");
        headerLayout->addWidget(minimize);
        headerLayout->addWidget(maximize);
        headerLayout->addWidget(close);
        root->addWidget(header);
        auto *content = new QPlainTextEdit(window);
        content->setReadOnly(true);
        content->setPlainText(body);
        root->addWidget(content, 1);
        window->show();
        auto *task = new QPushButton(title, this);
        task->setObjectName("task");
        taskLayout_->insertWidget(taskLayout_->count() - 1, task);
        connect(task, &QPushButton::clicked, this, [window] { window->setVisible(!window->isVisible()); window->raise(); });
        connect(minimize, &QPushButton::clicked, this, [window] { window->hide(); });
        connect(maximize, &QPushButton::clicked, this, [this, window] {
            window->setGeometry(18, 18, workspace_->width() - 36, workspace_->height() - 36);
            window->raise();
        });
        connect(close, &QPushButton::clicked, this, [window, task] { window->deleteLater(); task->deleteLater(); });
        window->raise();
    }

    void updateClock() {
        if (clock_) clock_->setText(QDateTime::currentDateTime().toString("ddd  HH:mm"));
        QTimer::singleShot(1000, this, [this] { updateClock(); });
    }

    QFrame *workspace_ = nullptr;
    QHBoxLayout *taskLayout_ = nullptr;
    QLabel *clock_ = nullptr;
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    EosDesktop desktop;
    desktop.show();
    if (argc == 3 && QString::fromLocal8Bit(argv[1]) == "--capture") {
        desktop.capture(QString::fromLocal8Bit(argv[2]));
    }
    return app.exec();
}
