package main

import (
    "github.com/gin-gonic/gin"
    "github.com/neo4j/neo4j-go-driver/v4/neo4j"
    "log"
    "os"
    "fmt"
    "github.com/joho/godotenv"
    "github.com/gin-contrib/cors"
    "net/http"

)

func newNeo4jDriver(uri, username, password string) neo4j.Driver {
    driver, err := neo4j.NewDriver(uri, neo4j.BasicAuth(username, password, ""))
    if err != nil {
        log.Fatalf("Error creating Neo4j driver: %v", err)
    }
    return driver
}

// Ensure the driver is closed when the application exits
func closeDriver(driver neo4j.Driver) {
    if err := driver.Close(); err != nil {
        log.Fatalf("Error closing Neo4j driver: %v", err)
    }
}

func main() {
    router := gin.Default()
    router.Use(cors.Default()) 
    // Load .env file
    err := godotenv.Load()
    if err != nil {
        log.Fatal("Error loading .env file")
    }

    // Initialize Neo4j driver
    uri := os.Getenv("NEO4J_URI")
    username := os.Getenv("NEO4J_USER")
    password := os.Getenv("NEO4J_PASSWORD")

    fmt.Println("URI:", uri)
    driver := newNeo4jDriver(uri, username, password)
    defer closeDriver(driver)

    router.GET("/data", func(c *gin.Context) {
        session := driver.NewSession(neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
        defer session.Close()

        greeting, err := session.ReadTransaction(func(tx neo4j.Transaction) (interface{}, error) {
            result, err := tx.Run("MATCH (n) RETURN n LIMIT 1", nil)
            if err != nil {
                return nil, err
            }
            if result.Next() {
                return result.Record().Values[0], nil
            }
            return "No data found", nil
        })

        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{"greeting": greeting})
    })

    router.POST("/query", func(c *gin.Context) {
        var queryData struct {
            Query      string                 `json:"query"`
            Parameters map[string]interface{} `json:"parameters"`
        }
        if err := c.BindJSON(&queryData); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
            return
        }

        resultData, err := executeNeo4jQuery(driver, queryData.Query, queryData.Parameters)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }

        c.JSON(http.StatusOK, gin.H{"result": resultData})
    })



    router.Run() // Listen and serve on 0.0.0.0:8080 (for windows "localhost:8080")
}

// Executes a read-only query against the Neo4j database
func executeNeo4jQuery(driver neo4j.Driver, query string, parameters map[string]interface{}) (interface{}, error) {
    session := driver.NewSession(neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
    defer session.Close()

    result, err := session.ReadTransaction(func(tx neo4j.Transaction) (interface{}, error) {
        result, err := tx.Run(query, parameters)
        if err != nil {
            return nil, err
        }

        var records []interface{}
        for result.Next() {
            records = append(records, result.Record().Values)
        }
        return records, nil
    })
    return result, err
}