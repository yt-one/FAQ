CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    parent_id BIGINT NULL COMMENT 'NULL means root category',
    name VARCHAR(100) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_categories_parent_id (parent_id)
);

CREATE TABLE faqs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category_id BIGINT NOT NULL,
    standard_question VARCHAR(500) NOT NULL,
    effective_start DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_end DATETIME NULL,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_faqs_category
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_faqs_category_id (category_id),
    INDEX idx_faqs_is_deleted (is_deleted)
);

CREATE TABLE similar_questions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    faq_id BIGINT NOT NULL,
    question_text VARCHAR(500) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(100) NOT NULL DEFAULT 'manual',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_similar_questions_faq
        FOREIGN KEY (faq_id) REFERENCES faqs(id) ON DELETE CASCADE,
    CONSTRAINT uk_similar_questions_faq_question UNIQUE (faq_id, question_text),
    INDEX idx_similar_questions_faq_active (faq_id, is_active)
);

CREATE TABLE tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_tags_name UNIQUE (name)
);

CREATE TABLE faq_tags (
    faq_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (faq_id, tag_id),
    CONSTRAINT fk_faq_tags_faq
        FOREIGN KEY (faq_id) REFERENCES faqs(id) ON DELETE CASCADE,
    CONSTRAINT fk_faq_tags_tag
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE faq_answers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    faq_id BIGINT NOT NULL,
    answer_type ENUM('text', 'rich_text', 'card') NOT NULL,
    answer_content TEXT NULL,
    card_id BIGINT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_faq_answers_faq
        FOREIGN KEY (faq_id) REFERENCES faqs(id) ON DELETE CASCADE,
    INDEX idx_faq_answers_faq_active (faq_id, is_active)
);
