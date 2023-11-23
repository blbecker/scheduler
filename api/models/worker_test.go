package models

import (
	"encoding/json"
	"fmt"
	"time"
)

func (ms *ModelSuite) Test_Worker_String() {
	w := Worker{
		GivenName:   "Bruce",
		FamilyName:  "Banner",
		DateOfBirth: time.Date(1990, 10, 28, 0, 0, 0, 0, time.UTC),
	}
	jw, _ := json.Marshal(w)
	ms.Equal(w.String(), string(jw))

	var ws Workers = []Worker{w}
	jws, _ := json.Marshal(ws)
	ms.Equal(ws.String(), string(jws))
}

func (ms *ModelSuite) Test_Worker_Validate() {
	w := Worker{}

	errors, err := w.Validate(ms.DB)
	ms.Nil(err)
	ms.Contains(errors.Errors, "given_name")
	ms.Contains(errors.Errors, "family_name")
	ms.Contains(errors.Errors, "date_of_birth")

}

func (ms *ModelSuite) Test_Worker_SaveAndRetrieve() {
	err := ms.CleanDB()
	ms.Nil(err)

	w := Worker{
		GivenName:   "Test",
		FamilyName:  "User",
		DateOfBirth: time.Now(),
	}
	errors, err := ms.DB.ValidateAndSave(&w)

	fmt.Println(errors)

	ms.Nil(err)
	ms.Empty(errors.Errors)

	retrievedWorker := Worker{}
	err = ms.DB.Find(&retrievedWorker, w.ID)

	ms.Nil(err)
	ms.Equal(w.GivenName, retrievedWorker.GivenName)
	ms.Equal(w.FamilyName, retrievedWorker.FamilyName)
}

func (ms *ModelSuite) Test_Worker_Retrieve() {
	ms.NoError(ms.CleanDB())
	ms.LoadFixture("many workers")

	worker := &Worker{}
	ms.NoError(ms.DB.Where("family_name = 'Banner'").Where("given_name = 'Bruce'").First(worker))

	ms.Equal("Bruce", worker.GivenName)
	ms.Equal("Banner", worker.FamilyName)
}
