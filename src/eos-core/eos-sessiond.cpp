#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>
#include <QString>
#include <iostream>

static bool write_state(const QString &root, const QJsonObject &state) {
    QDir().mkpath(root);
    const QString path = QDir(root).filePath("session-state.json");
    QFile temp(path + ".tmp");
    if (!temp.open(QIODevice::WriteOnly | QIODevice::Truncate)) return false;
    temp.write(QJsonDocument(state).toJson(QJsonDocument::Indented));
    temp.close();
    QFile::remove(path);
    return QFile::rename(temp.fileName(), path);
}

int main(int argc, char **argv) {
    QString root = QDir::temp().filePath("eos-session-dev");
    QString oobeStatePath;
    bool self_test = false;
    for (int i = 1; i < argc; ++i) {
        const QString arg = QString::fromLocal8Bit(argv[i]);
        if (arg == "--self-test") self_test = true;
        if (arg == "--root" && i + 1 < argc) root = QString::fromLocal8Bit(argv[++i]);
        if (arg == "--oobe-state" && i + 1 < argc) oobeStatePath = QString::fromLocal8Bit(argv[++i]);
    }
    if (self_test) {
        if (!oobeStatePath.isEmpty()) {
            QFile oobe(oobeStatePath);
            if (!oobe.open(QIODevice::ReadOnly)) return 3;
            const auto parsed = QJsonDocument::fromJson(oobe.readAll());
            if (!parsed.isObject() || parsed.object().value("completed_steps").toInt(0) < 3 || parsed.object().value("skipped").toBool(false)) return 4;
        }
        QJsonObject state;
        state.insert("schema", "eos-session-0.1");
        state.insert("user", "local-user");
        state.insert("oobe", "complete");
        state.insert("target", "eos-phone-shell");
        state.insert("lock_state", "locked-until-authenticated");
        if (!write_state(root, state)) return 2;
        std::cout << "eos-session-0.1 self-test root=" << root.toStdString() << " target=eos-phone-shell\n";
        return 0;
    }
    std::cout << "eos-sessiond: protocol eos-session-0.1; use --self-test\n";
    return 0;
}
