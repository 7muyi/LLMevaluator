# Table design

## Table Structure
### User
|filed|type|detail|constraint|
|---|---|---|---|
|**u_id**|INT|User id|PRIMARY KRY, AUTO_INCREMENT|
|u_name|VARCHAR(25)|User name|NOT NULL, UNIQUE|
|u_paddword|VARCHAR(30)|User password|NOT NULL|

### LLMs
|field|type|detail|constraint|
|---|---|---|---|
|**l_id**|INT|LLM id|PRIMARY KEY, AUTO_INCREMENT|
|l_name|VARCHAR(30)|LLM nikename|NOT NULL|
|l_url|VARCHAR(100)|API url|NOT NULL|
|l_return_format|VARCHAR(200)|The format returned by calling the API|NOT NULL|
|l_create_time|DATETIME|Creation time of LLM|DEFAULT now()|

### Prompt
|field|type|detail|constraint|
|---|---|---|---|
|**p_id**|INT|Prompt bank id|PRIMARY KEY, AUTO_INCREMENT|
|p_name|VARCHAR(30)|Prompt bank nikename|NOT NULL|
|p_file_path|VARCHAR(100)|The storage path of the prompt bank on the server|NOT NULL, UNIQUE|
|p_create_time|DATETIME|Creation time of prompt bank|DEFAULT now()|
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|

### Question
|field|type|detail|constraint|
|---|---|---|---|
|**q_id**|INT|Question bank id|PRIMARY KEY, AUTO_INCREMENT|
|q_name|VARCHAR(30)|Question bank nikename|NOT NULL|
|q_file_path|VARCHAR(100)|The storage path of the question bank on the server|NOT NULL, UNIQUE|
|q_create_time|DATETIME|Creation time of question bank|DEFAULT now()|
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|

### Test
|field|type|detail|constraint|
|---|---|---|---|
|t_id|INT|Test id|PRIMARY KEY, AUTO_INCREMENT|
|t_name|VARCHAR(30)|Test nikename|NOT NULL|
|t_create_time|DATETIME|Creation time of test|DEFAULT now()|
|t_status|ENUM("processing", "finish")|Test status|NOT NULL, DEFAULT "processing"|
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|
|p_id|INT|The id of the prompt bank used|FOREIGN KEY|
|q_id|INT|The id of the question bank used|FOREIGN KEY|
|l_id|INT|The id of the LLM being tested|FOREIGN KEY|

### Report
|field|type|detail|constraint|
|---|---|---|---|
|**r_id**|INT|Report file id|PRIMARY KEY, AUTO_INCREMENT|
|r_name|VARCHAR(30)|reprot file nikename|NOT NULL|
|r_file_path|VARCHAR(100)|The storage path of the report file on the server|NOT NULL, UNIQUE|
|r_create_time|DATETIME|Creation time of report file|DEFAULT now()|
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|

## MySQL Code
```SQL
-- Active: 1703057519402@@127.0.0.1@3306
CREATE DATABASE IF NOT EXISTS LLMevaluator
    DEFAULT CHARACTER SET = 'utf8mb4';

USE LLMevaluator;

-- User table
CREATE TABLE IF NOT EXISTS user (
    u_id INT PRIMARY KEY AUTO_INCREMENT,
    u_name VARCHAR(25) NOT NULL UNIQUE,
    u_password VARCHAR(30) NOT NULL
);

-- LLMs table
CREATE TABLE IF NOT EXISTS LLMs (
    l_id INT PRIMARY KEY AUTO_INCREMENT,
    l_name VARCHAR(30) NOT NULL,
    l_url VARCHAR(100) NOT NULL,
    l_return_format VARCHAR(200) NOT NULL,
    l_create_time DATETIME DEFAULT NOW()
);


-- Prompt table
CREATE TABLE IF NOT EXISTS Prompt (
    p_id INT PRIMARY KEY AUTO_INCREMENT,
    p_name VARCHAR(30) NOT NULL,
    p_file_path VARCHAR(100) NOT NULL UNIQUE,
    p_create_time DATETIME DEFAULT NOW(),
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES User(u_id)
);

-- Question table
CREATE TABLE IF NOT EXISTS Question (
    q_id INT PRIMARY KEY AUTO_INCREMENT,
    q_name VARCHAR(30) NOT NULL,
    q_file_path VARCHAR(100) NOT NULL UNIQUE,
    q_create_time DATETIME DEFAULT NOW(),
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES User(u_id)
);

-- Test table
CREATE TABLE IF NOT EXISTS Test (
    t_id INT PRIMARY KEY AUTO_INCREMENT,
    t_name VARCHAR(30) NOT NULL,
    t_create_time DATETIME DEFAULT NOW(),
    t_status ENUM('processing', 'finish') NOT NULL DEFAULT 'processing',
    u_id INT,
    p_id INT,
    q_id INT,
    l_id INT,
    FOREIGN KEY (u_id) REFERENCES User(u_id),
    FOREIGN KEY (p_id) REFERENCES Prompt(p_id),
    FOREIGN KEY (q_id) REFERENCES Question(q_id),
    FOREIGN KEY (l_id) REFERENCES LLMs(l_id)
);

-- Report table
CREATE TABLE IF NOT EXISTS Report (
    r_id INT PRIMARY KEY AUTO_INCREMENT,
    r_name VARCHAR(30) NOT NULL,
    r_file_path VARCHAR(100) NOT NULL UNIQUE,
    r_create_time DATETIME DEFAULT NOW(),
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES User(u_id)
);
```
