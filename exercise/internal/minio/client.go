// internal/minio/client.go
package minio

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"sync"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

var (
	instance *S3Client
	once     sync.Once
)

type S3Client struct {
	client *minio.Client
	bucket string
}

func NewS3Client(host string, accessKey string, secretKey string, secure bool, bucket string) (*S3Client, error) {
	var err error
	var client *minio.Client

	once.Do(func() {
		client, err = minio.New(host, &minio.Options{
			Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
			Secure: secure,
		})
		if err != nil {
			return
		}

		// Check if bucket exists, create if not
		exists, err := client.BucketExists(context.Background(), bucket)
		if err != nil {
			return
		}

		if !exists {
			err = client.MakeBucket(context.Background(), bucket, minio.MakeBucketOptions{})
			if err != nil {
				return
			}
		}

		instance = &S3Client{
			client: client,
			bucket: bucket,
		}
	})

	if err != nil {
		return nil, fmt.Errorf("failed to initialize S3 client: %w", err)
	}

	return instance, nil
}

func GetS3Client() (*S3Client, error) {
	if instance == nil {
		return nil, fmt.Errorf("S3Client not initialized yet. Expected call of NewS3Client beforehand")
	}
	return instance, nil
}

func (c *S3Client) Upload(ctx context.Context, objName string, data []byte) error {
	reader := bytes.NewReader(data)

	_, err := c.client.PutObject(ctx, c.bucket, objName, reader, int64(len(data)),
		minio.PutObjectOptions{
			ContentType: "text/plain",
		})
	if err != nil {
		return fmt.Errorf("failed to upload object %s: %w", objName, err)
	}

	return nil
}

func (c *S3Client) Download(ctx context.Context, objName string) ([]byte, error) {
	obj, err := c.client.GetObject(ctx, c.bucket, objName, minio.GetObjectOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to get object %s: %w", objName, err)
	}
	defer obj.Close()

	data, err := io.ReadAll(obj)
	if err != nil {
		return nil, fmt.Errorf("failed to read object %s: %w", objName, err)
	}

	return data, nil
}

func (c *S3Client) UploadExerciseDescription(ctx context.Context, exerciseID int, description string) error {
	objName := fmt.Sprintf("ex-%d.txt", exerciseID)
	return c.Upload(ctx, objName, []byte(description))
}

func (c *S3Client) DownloadExerciseDescription(ctx context.Context, exerciseID int) (string, error) {
	objName := fmt.Sprintf("ex-%d.txt", exerciseID)
	data, err := c.Download(ctx, objName)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// Для обратной совместимости с вашим кодом
func (c *S3Client) UploadExerciseDescriptionOld(exerciseID int, description string) error {
	return c.UploadExerciseDescription(context.Background(), exerciseID, description)
}

func (c *S3Client) DownloadExerciseDescriptionOld(exerciseID int) (string, error) {
	return c.DownloadExerciseDescription(context.Background(), exerciseID)
}
