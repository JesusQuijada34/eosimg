#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QString>
#include <iostream>

static bool append_log(const QString &root, const QString &service, const QString &message) {
    QDir().mkpath(root);
    QFile file(QDir(root).filePath("eos.log.jsonl"));
    if (!file.open(QIODevice::WriteOnly | QIODevice::Append)) return false;
    QJsonObject object;
    object.insert("schema", "eos-log-0.1");
    object.insert("timestamp", QDateTime::currentDateTimeUtc().toString(Qt::ISODateWithMs));
    object.insert("service", service);
    object.insert("message", message);
    file.write(QJsonDocument(object).toJson(QJsonDocument::Compact) + "\n");
    return true;
}

int main(int argc, char **argv) {
    QString root = QDir::temp().filePath("eos-log-dev");
    bool self_test = false;
    for (int i = 1; i < argc; ++i) {
        const QString arg = QString::fromLocal8Bit(argv[i]);
        if (arg == "--self-test") self_test = true;
        if (arg == "--root" && i + 1 < argc) root = QString::fromLocal8Bit(argv[++i]);
    }
    if (self_test) {
        if (!append_log(root, "eos-logd", "structured logging ready")) return 2;
        if (!append_log(root, "eos-serviced", "service graph accepted")) return 2;
        std::cout << "eos-log-0.1 self-test root=" << root.toStdString() << " entries=2\n";
        return 0;
    }
    std::cout << "eos-logd: protocol eos-log-0.1; use --self-test\n";
    return 0;
}
