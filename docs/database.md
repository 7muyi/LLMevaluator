# Table design

## Table Structure
### user
|filed|type|detail|constraint|
|---|---|---|---|
|**u_id**|INT|User id|PRIMARY KRY, AUTO_INCREMENT|
|u_name|VARCHAR(25)|User name|NOT NULL, UNIQUE|
|u_password|VARCHAR(30)|User password|NOT NULL|
|u_email|VARCHAR(50)|User email|UNIQUE|

### LLM
|field|type|detail|constraint|
|---|---|---|---|
|**l_id**|INT|LLM id|PRIMARY KEY, AUTO_INCREMENT|
|l_name|VARCHAR(30)|LLM nikename|NOT NULL|
|l_url|VARCHAR(100)|API url|NOT NULL|
|l_access_token|VARCHAR(255)|Access token of API||
|l_return_format|VARCHAR(200)|The format returned by calling the API|NOT NULL|
|l_create_time|DATETIME|Creation time of LLM|DEFAULT now()|
|u_id|INT|User id|FOREIGN KEY|

### prompt
|field|type|detail|constraint|
|---|---|---|---|
|**p_id**|INT|Prompt bank id|PRIMARY KEY, AUTO_INCREMENT|
|p_name|VARCHAR(30)|Prompt bank nikename|NOT NULL|
|p_file_path|VARCHAR(100)|The storage path of the prompt bank on the server|NOT NULL, UNIQUE|
|p_create_time|DATETIME|Creation time of prompt bank|DEFAULT now()|
|p_num_row|INT|The number of rows||
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|

### question
|field|type|detail|constraint|
|---|---|---|---|
|**q_id**|INT|Question bank id|PRIMARY KEY, AUTO_INCREMENT|
|q_name|VARCHAR(30)|Question bank nikename|NOT NULL|
|q_file_path|VARCHAR(100)|The storage path of the question bank on the server|NOT NULL, UNIQUE|
|q_create_time|DATETIME|Creation time of question bank|DEFAULT now()|
|q_num_row|INT|The number of rows||
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|

### test
|field|type|detail|constraint|
|---|---|---|---|
|t_id|INT|Test id|PRIMARY KEY, AUTO_INCREMENT|
|t_name|VARCHAR(30)|Test nikename|NOT NULL|
|t_create_time|DATETIME|Creation time of test|DEFAULT now()|
|t_status|ENUM("processing", "finish", "error")|Test status|NOT NULL, DEFAULT "processing"|
|t_result_file|VARCHAR(64)|The path of result file||
|u_id|INT|The id of the user it belongs to|FOREIGN KEY|
|p_id|INT|The id of the prompt bank used|FOREIGN KEY|
|q_id|INT|The id of the question bank used|FOREIGN KEY|
|l_id|INT|The id of the LLM being tested|FOREIGN KEY|
## MySQL Code
```SQL

CREATE DATABASE IF NOT EXISTS LLMevaluator
    DEFAULT CHARACTER SET = 'utf8mb4';

USE LLMevaluator;

-- User table
CREATE TABLE IF NOT EXISTS user (
    u_id INT PRIMARY KEY AUTO_INCREMENT,
    u_name VARCHAR(25) NOT NULL UNIQUE,
    u_password VARCHAR(30) NOT NULL,
    u_email VARCHAR(50) UNIQUE,
    u_pic_path VARCHAR(50) DEFAULT "default_pic.png"
);

-- LLMs table
CREATE TABLE IF NOT EXISTS LLM (
    l_id INT PRIMARY KEY AUTO_INCREMENT,
    l_name VARCHAR(30) NOT NULL,
    l_url VARCHAR(100) NOT NULL,
    l_access_token VARCHAR(255),
    l_return_format VARCHAR(200) NOT NULL,
    l_create_time DATETIME DEFAULT NOW(),
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES user(u_id)
);


-- Prompt table
CREATE TABLE IF NOT EXISTS prompt (
    p_id INT PRIMARY KEY AUTO_INCREMENT,
    p_name VARCHAR(30) NOT NULL,
    p_file_path VARCHAR(100) NOT NULL UNIQUE,
    p_create_time DATETIME DEFAULT NOW(),
    p_num_row INT,
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES user(u_id)
);

-- Question table
CREATE TABLE IF NOT EXISTS question (
    q_id INT PRIMARY KEY AUTO_INCREMENT,
    q_name VARCHAR(30) NOT NULL,
    q_file_path VARCHAR(100) NOT NULL UNIQUE,
    q_create_time DATETIME DEFAULT NOW(),
    q_num_row INT,
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES user(u_id)
);

-- Test table
CREATE TABLE IF NOT EXISTS test (
    t_id INT PRIMARY KEY AUTO_INCREMENT,
    t_name VARCHAR(30) NOT NULL,
    t_create_time DATETIME DEFAULT NOW(),
    t_status ENUM('processing', 'finish', 'error') NOT NULL DEFAULT 'processing',
    t_result_file VARCHAR(64),
    u_id INT,
    p_id INT,
    q_id INT,
    l_id INT,
    FOREIGN KEY (u_id) REFERENCES user(u_id),
    FOREIGN KEY (p_id) REFERENCES prompt(p_id),
    FOREIGN KEY (q_id) REFERENCES question(q_id),
    FOREIGN KEY (l_id) REFERENCES LLM(l_id)
);
```
