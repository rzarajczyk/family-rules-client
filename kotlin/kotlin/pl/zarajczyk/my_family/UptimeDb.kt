package pl.zarajczyk.my_family

import org.apache.commons.lang3.SystemUtils
import org.springframework.stereotype.Service
import java.io.File
import java.time.Duration
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.*

@Service
class UptimeDb {
    fun update(apps: List<String>, tickSeconds: Int) {
        val file = getPropertiesFile()
        val properties = file.loadAsProperties()

        properties.inc("screen-time", tickSeconds)
        apps.forEach {
            properties.inc("application:$it", tickSeconds)
        }

        file.saveProperties(properties)
    }

    fun get(): Usage {
        val properties = getPropertiesFile().loadAsProperties()
        return Usage(
            screenTime = properties.getDuration("screen-time"),
            applications = properties.stringPropertyNames()
                .filter { it.startsWith("application:") }
                .associateWith { properties.getDuration(it) }
                .mapKeys { (k,_) -> k.removePrefix("application:") }
        )
    }

    private fun getPropertiesFile(): File {
        val data = File(SystemUtils.getUserHome(), ".my-family")
        data.mkdirs()
        val now = Instant.now()
        val today = DateTimeFormatter.ofPattern("yyyy-MM-dd").withZone(ZoneId.systemDefault()).format(now)

        val file = File(data, "$today")
        file.createNewFile()
        return file
    }

    private fun File.loadAsProperties(): Properties {
        val properties = Properties()
        this.inputStream().use { properties.load(it) }
        return properties
    }

    private fun File.saveProperties(properties: Properties) {
        this.outputStream().use { properties.store(it, "my-family") }
    }

    private fun Properties.inc(name: String, count: Int) {
        val current = getLong(name)
        setProperty(name, "${current + count}")
    }

    private fun Properties.getLong(name: String) = getProperty(name, "0").toLong()
    private fun Properties.getDuration(name: String) = Duration.ofSeconds(getLong(name))
}

data class Usage(
    val screenTime: Duration,
    val applications: Map<String, Duration>
)