package model

type Impression struct {
	UserID    string `json:"user_id"`
	EventID   string `json:"event_id"`
	Timestamp string `json:"timestamp"`
}
