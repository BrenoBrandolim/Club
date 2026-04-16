create database BancoClube;
use BancoClube;

CREATE TABLE usuarios (
	id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    nome VARCHAR(150) NOT NULL,
    nickname VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios_comandas (
	id INT AUTO_INCREMENT PRIMARY KEY,
    comanda_id INT NOT NULL UNIQUE,
    usuario_id INT NOT NULL,
    data_vinculacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    processada BOOLEAN DEFAULT FALSE,
    
    INDEX idx_usuario_comandas(usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE pontos (
	id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo ENUM('ganho', 'gasto') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    comanda_id INT, -- Opcional
    descricao VARCHAR(255),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_usuario_pontos(usuario_id),
    INDEX idx_comanda_pontos(comanda_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE produtos_clube (
	id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    foto_url VARCHAR(255) NOT NULL,
    pontos_necessarios DECIMAL(10,2) NOT NULL,
    preco_dinheiro DECIMAL(10,2),
    ativo BOOLEAN DEFAULT TRUE,
    item_id INT UNIQUE
);

CREATE TABLE resgates (
	id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    produto_id INT NOT NULL,
    comanda_id INT NOT NULL,
    pontos_gastos DECIMAL(10,2) NOT NULL,
    tipo ENUM('local', 'viagem') NOT NULL,
    status ENUM('pendente','entregue') DEFAULT 'pendente',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    
	INDEX idx_usuario_resgates(usuario_id),
    INDEX idx_comanda_resgates(comanda_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos_clube(id)
);

INSERT INTO usuarios (nome, nickname, senha_hash)
VALUES ('Breno', 'light', '123456');

INSERT INTO pontos (usuario_id, tipo, valor, descricao)
VALUES (1, 'ganho', 10000, 'Carga manual para teste');
