package models

import (
	"encoding/json"
	"time"

	"github.com/gobuffalo/pop/v6"
	"github.com/gobuffalo/validate/v3"
	"github.com/gobuffalo/validate/v3/validators"
	"github.com/gofrs/uuid"
)

// Worker is used by pop to map your workers database table to your go code.
type Worker struct {
	ID          uuid.UUID `json:"id" db:"id"`
	GivenName   string    `json:"given_name" db:"given_name"`
	FamilyName  string    `json:"family_name" db:"family_name"`
	DateOfBirth time.Time `json:"date_of_birth" db:"date_of_birth"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// String is not required by pop and may be deleted
func (w Worker) String() string {
	jw, _ := json.Marshal(w)
	return string(jw)
}

// Workers is not required by pop and may be deleted
type Workers []Worker

// String is not required by pop and may be deleted
func (w Workers) String() string {
	jw, _ := json.Marshal(w)
	return string(jw)
}

// Validate gets run every time you call a "pop.Validate*" (pop.ValidateAndSave, pop.ValidateAndCreate, pop.ValidateAndUpdate) method.
// This method is not required and may be deleted.
func (w *Worker) Validate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.Validate(
		&validators.StringIsPresent{Field: w.GivenName, Name: "GivenName"},
		&validators.StringIsPresent{Field: w.FamilyName, Name: "FamilyName"},
		&validators.TimeIsPresent{Field: w.DateOfBirth, Name: "DateOfBirth"},
	), nil
}

// ValidateCreate gets run every time you call "pop.ValidateAndCreate" method.
// This method is not required and may be deleted.
func (w *Worker) ValidateCreate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

// ValidateUpdate gets run every time you call "pop.ValidateAndUpdate" method.
// This method is not required and may be deleted.
func (w *Worker) ValidateUpdate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}
