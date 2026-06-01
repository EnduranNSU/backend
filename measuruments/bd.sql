CREATE TABLE user_info (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height INTEGER NOT NULL,
    date DATE NOT NULL,
    age INTEGER NOT NULL,
    user_id UUID NOT NULL
);


CREATE INDEX idx_user_info_user_id ON user_info(user_id);
CREATE INDEX idx_user_info_user_id_date ON user_info(user_id, date DESC);