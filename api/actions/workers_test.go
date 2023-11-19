package actions

import (
	"encoding/json"
	"fmt"
	"github.com/blbecker/scheduler/api/models"
	"io/ioutil"
	"net/http"
	"time"
)

func (as *ActionSuite) Test_WorkersResource_List() {
	as.NoError(as.CleanDB())
	as.LoadFixture("many workers")

	// Find a worker we know is in the db
	w := &models.Workers{}
	dbErr := as.DB.All(w)
	if dbErr != nil {
		fmt.Println(dbErr)
	}
	as.NoError(dbErr)

	// Request that worker from the API
	res := as.JSON("/workers").Get()
	// Response should be Content-Type == JSON
	as.Contains(res.Header().Get("Content-Type"), "application/json")

	// Unmarshal the response into a new set of workers
	responseWorker := &models.Workers{}

	resBody, err := ioutil.ReadAll(res.Body)
	as.NoError(err)

	err = json.Unmarshal(resBody, responseWorker)
	as.NoError(err)
	as.NotEmpty(*responseWorker)
	as.NotZero(len(*responseWorker))
	as.Equal(len(*w), len(*responseWorker))
}

func (as *ActionSuite) Test_WorkersResource_Show() {
	as.NoError(as.CleanDB())
	as.LoadFixture("many workers")

	// Find a worker we know is in the db
	w := &models.Worker{}
	dbErr := as.DB.First(w)
	if dbErr != nil {
		fmt.Println(dbErr)
	}
	as.NoError(dbErr)

	// Request that worker from the API
	res := as.JSON(fmt.Sprintf("/workers/%s", w.ID)).Get()
	// Response should be Content-Type == JSON
	as.Contains(res.Header().Get("Content-Type"), "application/json")

	// Unmarshal the response into a new worker
	responseWorker := &models.Worker{}

	resBody, err := ioutil.ReadAll(res.Body)
	as.NoError(err)

	err = json.Unmarshal(resBody, responseWorker)
	as.NoError(err)
	as.NotEmpty(responseWorker.ID)
	as.Equal(responseWorker.ID, w.ID)
}

func (as *ActionSuite) Test_WorkersResource_Create() {
	// Post a test worker model
	as.NoError(as.CleanDB())

	w := &models.Worker{FamilyName: "Stark", GivenName: "Tony", DateOfBirth: time.Now()} // make a POST /workers request
	res := as.JSON("/workers").Post(w)

	// Response should be Content-Type == JSON
	as.Contains(res.Header().Get("Content-Type"), "application/json")

	responseWorker := &models.Worker{}

	resBody, err := ioutil.ReadAll(res.Body)
	as.NoError(err)

	err = json.Unmarshal(resBody, responseWorker)
	as.NoError(err)
	as.NotEmpty(responseWorker.ID)

	rw := &models.Worker{}
	// retrieve the first Widget from the database
	as.NoError(as.DB.Where(fmt.Sprintf("family_name = '%s'", w.FamilyName)).Where(fmt.Sprintf("given_name = '%s'", w.GivenName)).First(rw))
	as.NotZero(rw.ID)

	// assert the Worker was saved correctly
	as.Equal("Stark", rw.FamilyName)
	as.Equal("Tony", rw.GivenName)
}

func (as *ActionSuite) Test_WorkersResource_Update() {
	as.NoError(as.CleanDB())
	as.LoadFixture("many workers")

	// Find Tony
	tony := &models.Worker{}
	dbErr := as.DB.Where("family_name = 'Stark'").Where("given_name = 'Tony'").First(tony)
	as.NoError(dbErr)

	as.Equal("Tony", tony.GivenName)
	as.Equal("Stark", tony.FamilyName)

}

func (as *ActionSuite) Test_WorkersResource_Destroy() {
	as.NoError(as.CleanDB())
	as.LoadFixture("many workers")

	// Find a worker we know is in the db
	w := &models.Worker{}
	as.NoError(as.DB.First(w))

	// Delete that worker from the API
	res := as.JSON(fmt.Sprintf("/workers/%s", w.ID)).Delete()

	// Response should be Content-Type == JSON
	as.Contains(res.Header().Get("Content-Type"), "application/json")
	as.Equal(http.StatusOK, res.Code)

	// Unmarshal the response into a new worker
	responseWorker := &models.Worker{}

	resBody, err := ioutil.ReadAll(res.Body)
	as.NoError(err)

	err = json.Unmarshal(resBody, responseWorker)
	as.NoError(err)
	as.NotEmpty(responseWorker.ID)
	as.Equal(responseWorker.ID, w.ID)

	// Attempt to fetch the worker we deleted
	fetchedWorker := &models.Worker{}
	err = as.DB.Find(fetchedWorker, w.ID)
	as.NotNil(err)

	fmt.Println(err)

}
