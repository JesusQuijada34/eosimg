#include <QApplication>
#include <QDateTime>
#include <QDialog>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QMainWindow>
#include <QPushButton>
#include <QScreen>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>

class EosPhoneShell final : public QMainWindow {
public:
    EosPhoneShell() {
        setWindowTitle("EOS Phone Shell");
        setMinimumSize(390, 780);
        resize(430, 860);
        setStyleSheet(R"(
            QMainWindow, QWidget { background: #101522; color: #f6f8ff; }
            QLabel#status { color: #b5c4e5; font-size: 13px; padding: 6px 14px; }
            QLabel#title { font-size: 27px; font-weight: 700; padding: 4px 18px 12px; }
            QPushButton[class="app"] { background: #1d2940; border: 1px solid #2d3c5a; border-radius: 18px; padding: 18px 7px; font-size: 14px; }
            QPushButton[class="app"]:hover { background: #2a3c60; }
            QPushButton[class="dock"] { background: #273553; border: none; border-radius: 20px; padding: 15px 5px; font-size: 13px; }
            QLabel#home { background: #314f89; border-radius: 3px; min-height: 4px; max-height: 4px; }
        )");

        auto *central = new QWidget(this);
        auto *root = new QVBoxLayout(central);
        root->setContentsMargins(14, 10, 14, 12);
        root->setSpacing(6);

        auto *status = new QLabel(this);
        status->setObjectName("status");
        status->setAlignment(Qt::AlignRight);
        root->addWidget(status);

        auto *title = new QLabel("Etternhall", this);
        title->setObjectName("title");
        root->addWidget(title);

        auto *grid = new QGridLayout();
        grid->setHorizontalSpacing(10);
        grid->setVerticalSpacing(10);
        const QStringList apps = {"Archivos", "Terminal", "Ajustes", "Cámara", "Música", "EosLang", "Paquetes", "Sensores"};
        for (int i = 0; i < apps.size(); ++i) {
            auto *button = new QPushButton(apps.at(i), this);
            button->setProperty("class", "app");
            button->setObjectName("app");
            button->setAccessibleName("Abrir " + apps.at(i));
            grid->addWidget(button, i / 2, i % 2);
        }
        root->addLayout(grid, 1);

        auto *dock = new QHBoxLayout();
        dock->setSpacing(8);
        for (const auto &name : {QString("Inicio"), QString("Buscar"), QString("Biblioteca"), QString("Teclado")}) {
            auto *button = new QPushButton(name, this);
            button->setProperty("class", "dock");
            button->setObjectName("dock");
            dock->addWidget(button, 1);
            if (name == "Teclado") {
                connect(button, &QPushButton::clicked, this, [this] {
                    auto *dialog = new QDialog(this);
                    dialog->setAttribute(Qt::WA_DeleteOnClose);
                    dialog->setWindowTitle("EOS Virtual Keyboard");
                    dialog->setMinimumWidth(360);
                    auto *layout = new QVBoxLayout(dialog);
                    auto *input = new QLineEdit(dialog);
                    input->setPlaceholderText("Escribe con el teclado EOS");
                    layout->addWidget(input);
                    auto *keys = new QGridLayout();
                    const QString rows[] = {"QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"};
                    for (int row = 0; row < 3; ++row) {
                        for (int column = 0; column < rows[row].size(); ++column) {
                            const QString key = rows[row].mid(column, 1);
                            auto *keyButton = new QPushButton(key, dialog);
                            keyButton->setProperty("class", "app");
                            connect(keyButton, &QPushButton::clicked, dialog, [input, key] { input->insert(key); });
                            keys->addWidget(keyButton, row, column);
                        }
                    }
                    auto *space = new QPushButton("Espacio", dialog);
                    space->setProperty("class", "dock");
                    connect(space, &QPushButton::clicked, dialog, [input] { input->insert(" "); });
                    keys->addWidget(space, 3, 0, 1, 10);
                    layout->addLayout(keys);
                    dialog->show();
                });
            }
        }
        root->addLayout(dock);
        auto *home = new QLabel(this);
        home->setObjectName("home");
        home->setFixedWidth(110);
        root->addWidget(home, 0, Qt::AlignHCenter);

        setCentralWidget(central);
        auto *clock = new QTimer(this);
        connect(clock, &QTimer::timeout, this, [status] {
            status->setText(QDateTime::currentDateTime().toString("ddd  HH:mm"));
        });
        clock->start(1000);
        status->setText(QDateTime::currentDateTime().toString("ddd  HH:mm"));
    }
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    EosPhoneShell shell;
    shell.show();
    return app.exec();
}
