package grifts

import (
	"github.com/blbecker/scheduler/api/actions"

	"github.com/gobuffalo/buffalo"
)

func init() {
	buffalo.Grifts(actions.App())
}
