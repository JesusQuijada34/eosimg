#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QString>
#include <iostream>

static bool atomic_write(const QString &root, const QString &relative, const QJsonObject &object) {
    const QDir base(root);
    const QString path = base.filePath(relative);
    QDir().mkpath(QFileInfo(path).absolutePath());
    QFile temp(path + ".tmp");
    if (!temp.open(QIODevice::WriteOnly | QIODevice::Truncate)) return false;
    temp.write(QJsonDocument(object).toJson(QJsonDocument::Indented));
    temp.close();
    QFile::remove(path);
    return QFile::rename(temp.fileName(), path);
}

int main(int argc, char **argv) {
    QString root = QDir::temp().filePath("eos-storage-dev");
    bool self_test = false;
    for (int i = 1; i < argc; ++i) {
        const QString arg = QString::fromLocal8Bit(argv[i]);
        if (arg == "--self-test") self_test = true;
        if (arg == "--root" && i + 1 < argc) root = QString::fromLocal8Bit(argv[++i]);
    }
    if (self_test) {
        QJsonObject state;
        state.insert("schema", "eos-storage-0.1");
        state.insert("data", "eos://data");
        state.insert("cache", "eos://cache");
        state.insert("profiles", "eos://profiles");
        state.insert("external_storage", "permission-required");
        if (!atomic_write(root, "system/storage-state.json", state)) return 2;
        std::cout << "eos-storage-0.1 self-test root=" << root.toStdString() << " atomic=true\n";
        return 0;
    }
    std::cout << "eos-storaged: protocol eos-storage-0.1; use --self-test\n";
    return 0;
}
