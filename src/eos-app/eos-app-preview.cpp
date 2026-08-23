#include <QApplication>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QMainWindow>
#include <QPushButton>
#include <QStackedWidget>
#include <QStatusBar>
#include <QTimer>
#include <QVBoxLayout>
#include <QString>

class NotesPreview final : public QMainWindow {
public:
    NotesPreview() {
        setWindowTitle("EOS Notes — Activity Preview");
        resize(430, 820);
        setStyleSheet(R"(
            QMainWindow, QWidget { background: #101522; color: #f6f8ff; }
            QLabel#bar { background: #1d2940; font-size: 20px; font-weight: 700; padding: 18px; }
            QLabel#caption { color: #b5c4e5; padding: 12px; }
            QPushButton { background: #314f89; color: white; border: none; border-radius: 12px; padding: 14px; font-size: 15px; }
            QPushButton#back { background: transparent; border: 1px solid #4c638e; }
            QLineEdit { background: #1d2940; color: white; border: 1px solid #4c638e; border-radius: 10px; padding: 14px; }
        )");
        stack_ = new QStackedWidget(this);
        stack_->addWidget(homePage());
        stack_->addWidget(editorPage());
        setCentralWidget(stack_);
        showActivity("notes.home");
    }

    void showActivity(const QString &activity) {
        if (activity == "notes.editor") {
            stack_->setCurrentIndex(1);
        } else {
            stack_->setCurrentIndex(0);
        }
        current_ = activity;
        statusBar()->showMessage("activity=" + current_ + " lifecycle=resumed");
    }

    void capture(const QString &path) {
        QTimer::singleShot(250, this, [this, path] { grab().save(path, "PNG"); qApp->quit(); });
    }

private:
    QWidget *homePage() {
        auto *page = new QWidget;
        auto *layout = new QVBoxLayout(page);
        auto *bar = new QLabel("Mis notas");
        bar->setObjectName("bar");
        layout->addWidget(bar);
        auto *caption = new QLabel("notes.home • actividad principal\nSelecciona una nota o crea una nueva");
        caption->setObjectName("caption");
        layout->addWidget(caption);
        auto *note = new QPushButton("Bienvenido a EOS\nNota local de ejemplo");
        note->setAccessibleName("Abrir nota");
        layout->addWidget(note);
        auto *newNote = new QPushButton("+  Nueva nota");
        layout->addWidget(newNote);
        layout->addStretch();
        auto *gesture = new QLabel("Swipe-left → notes.editor");
        gesture->setObjectName("caption");
        layout->addWidget(gesture);
        connect(note, &QPushButton::clicked, this, [this] { showActivity("notes.editor"); });
        connect(newNote, &QPushButton::clicked, this, [this] { showActivity("notes.editor"); });
        return page;
    }

    QWidget *editorPage() {
        auto *page = new QWidget;
        auto *layout = new QVBoxLayout(page);
        auto *row = new QHBoxLayout;
        auto *back = new QPushButton("‹  Atrás");
        back->setObjectName("back");
        auto *bar = new QLabel("Editar nota");
        bar->setObjectName("bar");
        row->addWidget(back);
        row->addWidget(bar, 1);
        layout->addLayout(row);
        auto *caption = new QLabel("notes.editor • actividad secundaria privada");
        caption->setObjectName("caption");
        layout->addWidget(caption);
        auto *editor = new QLineEdit;
        editor->setPlaceholderText("Escribe una nota…");
        layout->addWidget(editor);
        auto *save = new QPushButton("Guardar");
        layout->addWidget(save);
        layout->addStretch();
        connect(back, &QPushButton::clicked, this, [this] { showActivity("notes.home"); });
        connect(save, &QPushButton::clicked, this, [this] { statusBar()->showMessage("eos.storage.append → nota guardada"); });
        return page;
    }

    QStackedWidget *stack_ = nullptr;
    QString current_;
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    NotesPreview preview;
    preview.show();
    if (argc == 3 && QString::fromLocal8Bit(argv[1]) == "--capture") {
        preview.capture(QString::fromLocal8Bit(argv[2]));
    }
    if (argc == 4 && QString::fromLocal8Bit(argv[1]) == "--capture-activity") {
        preview.showActivity(QString::fromLocal8Bit(argv[2]));
        preview.capture(QString::fromLocal8Bit(argv[3]));
    }
    return app.exec();
}
