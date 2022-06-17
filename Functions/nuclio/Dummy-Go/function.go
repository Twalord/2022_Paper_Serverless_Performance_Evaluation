/*
Copyright 2017 The Nuclio Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

import (
	"github.com/nuclio/nuclio-sdk-go"
)

func Handler(context *nuclio.Context, event nuclio.Event) (interface{}, error) {
	//context.Logger.Info("This is an unstrucured %s", "log")
    
    
    // Construct image from input
    b := event.GetBody()

    // Reverse bytes of input
    for i,j := 0, len(b) - 1; i<j; i,j = i+1, j-1 {
        b[i],b[j] = b[j], b[i]
    }
    
	return nuclio.Response{
		StatusCode:  200,
		ContentType: "application/text",
        Body:        b,
    }, nil
}
