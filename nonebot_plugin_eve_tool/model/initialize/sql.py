class Sql:
    eve_type_sql: str = """
            CREATE TABLE eve_type (
                id                   INT          NOT NULL COMMENT '物品ID'
                    PRIMARY KEY,
                name                 VARCHAR(200) NULL COMMENT '物品名称',
                name_en              VARCHAR(200) NULL COMMENT '物品名称英文',
                description          LONGTEXT     NULL COMMENT '物品描述',
                description_en       LONGTEXT     NULL COMMENT '物品描述英文',
                group_id             INT          NULL COMMENT '分组ID',
                group_name           VARCHAR(200) NULL COMMENT '分组名称',
                group_name_en        VARCHAR(200) NULL COMMENT '分组名称英文',
                meta_group_id        INT          NULL COMMENT '元分组ID',
                meta_group_name      VARCHAR(200) NULL COMMENT '元分组名称',
                meta_group_name_en   VARCHAR(200) NULL COMMENT '元分组名称英文',
                market_group_id      INT          NULL COMMENT '市场分组ID',
                market_group_name    VARCHAR(200) NULL COMMENT '市场分组名称',
                market_group_name_en VARCHAR(200) NULL COMMENT '市场分组名称英文',
                category_id          INT          NULL COMMENT '分类ID',
                category_name        VARCHAR(200) NULL COMMENT '分类名称',
                category_name_en     VARCHAR(200) NULL COMMENT '分类名称中文',
                create_time          TIMESTAMP    NULL
            )
            """
    listener_sql: str = """
        create table listener
    (
        id                 int auto_increment
            primary key,
        type               enum ('char', 'corp', 'alliance', 'high') not null,
        entity_id          varchar(255)   default '0'                not null,
        push_type          enum ('group', 'friend')                  not null,
        push_to            varchar(255)                              not null,
        attack_value_limit decimal(14, 2) default 15000000.00        not null,
        victim_value_limit decimal(14, 2) default 30000000.00        not null,
        title              varchar(255)                              not null
    )"""
    high_listener_sql: str = """
        CREATE TABLE high_listener (
        id INT PRIMARY KEY AUTO_INCREMENT,
        high_value_limit DECIMAL(14,2) DEFAULT 18000000000.00,
        push_type VARCHAR(255) NOT NULL,
        push_to VARCHAR(255) NOT NULL
    )"""
    group_index: str = "CREATE INDEX idx_group_id ON eve_type (group_id)"
    market_group_index: str = "CREATE INDEX idx_market_group_id ON eve_type (market_group_id)"

    alias_items: str = """
        CREATE TABLE alias_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        alias VARCHAR(255) NOT NULL,
        item VARCHAR(255) NOT NULL
    )
    """

    set_limit_time: str = "SET GLOBAL regexp_time_limit=10240;"

