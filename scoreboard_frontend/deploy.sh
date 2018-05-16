#!/bin/sh

# Allow BUILD=prod to be set.
if [ -z "$BUILD" ]; then
    BUILD=dev
elif [[ $BUILD != "prod" ]]; then
    echo "Only BUILD=prod is supported. Goodbye!"
    exit 1
fi

# Production safety check
if [[ $BUILD == "prod" ]]; then
    echo "Are you sure you want to deploy to production? (y|N) "
    read response
    if [[ $response != "y" ]]; then
        echo "Goodbye!"
        exit 2
    fi
fi

./node_modules/.bin/react-scripts build \
  && rm build/static/*/*.map \
  && rm build/asset-manifest.json \
  && rm build/service-worker.js \
  && find build/static -regex '.*\.[cj]ss*' -exec sed -i '' '/^\/[/*]# sourceMappingURL/ d' {} \;
