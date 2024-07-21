package pl.zarajczyk.my_family

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.scheduling.annotation.EnableScheduling

@SpringBootApplication
@EnableScheduling
class MyFamilyApplication

fun main(args: Array<String>) {
    runApplication<MyFamilyApplication>(*args)
}
