# Sugarjazy walkthrough


## Default log view (beurk)

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators
```

## Log viewing with sugarjazy (yay)

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators | sugarjazy
```

## Stream log vieweing

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators | sugarjazy -s
```


## Filter levels

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators | sugarjazy --filter-level error
```

## Filter multiple levels

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators | sugarjazy --filter-level debug,error
```


## Syntax highlighting

```bash
kubectl logs deployment/openshift-pipelines-operator -n openshift-operators | sugarjazy -r "TektonConfig"
```

## Kail

<https://github.com/boz/kail>


```bash
kail --since=1h -n openshift-operators|sugarjazy -s --kail
```


## Kail no prefix container


```bash
kail --since=1h -n openshift-operators|sugarjazy -s --kail --kail-no-prefix
```
